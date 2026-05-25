"""
Forward Chaining Inference Engine with Conflict Resolution
"""

from typing import Dict, List, Any, Optional
from .knowledge_base import KnowledgeBase, Rule, Crop


class WorkingMemory:
    """Stores current facts during inference"""
    
    def __init__(self):
        self.facts: Dict[str, Any] = {}
        self.certainties: Dict[str, float] = {}
        self.rule_trace: List[Dict] = []
    
    def add_fact(self, fact_name: str, value: Any, certainty: float, source_rule_id: str = None):
        """Add or update a fact in working memory"""
        
        # Handle adjustments to existing scores
        if isinstance(value, dict) and "adjustment" in value:
            if fact_name in self.facts:
                if isinstance(self.facts[fact_name], dict):
                    # FIX: Ensure the existing fact has an adjustment key
                    if "adjustment" not in self.facts[fact_name]:
                        # Preserve original value if it exists
                        if "original" not in self.facts[fact_name]:
                            self.facts[fact_name]["original"] = 0
                        self.facts[fact_name]["adjustment"] = 0
                    
                    # Accumulate adjustment
                    self.facts[fact_name]["adjustment"] += value["adjustment"]
                else:
                    # Convert existing non-dict to dict with adjustment
                    original_value = self.facts[fact_name]
                    self.facts[fact_name] = {
                        "original": original_value,
                        "adjustment": value["adjustment"]
                    }
                # Update certainty (take max)
                self.certainties[fact_name] = max(certainty, self.certainties.get(fact_name, 0))
            else:
                # New fact with adjustment
                self.facts[fact_name] = {
                    "adjustment": value["adjustment"]
                }
                self.certainties[fact_name] = certainty
        else:
            # Regular fact assignment
            self.facts[fact_name] = value
            self.certainties[fact_name] = certainty
        
        if source_rule_id:
            self.rule_trace.append({
                "fact": fact_name,
                "value": value,
                "rule": source_rule_id,
                "certainty": certainty
            })
    
    def get_fact(self, fact_name: str) -> Optional[Any]:
        """Get a fact from working memory"""
        return self.facts.get(fact_name)
    
    def get_adjustment(self, fact_name: str) -> float:
        """Get accumulated adjustment for a fact"""
        fact = self.facts.get(fact_name)
        if fact and isinstance(fact, dict) and "adjustment" in fact:
            return fact["adjustment"]
        return 0.0
    
    def get_certainty(self, fact_name: str) -> float:
        """Get certainty factor for a fact"""
        return self.certainties.get(fact_name, 0.0)


class InferenceEngine:
    """Forward chaining inference engine"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.working_memory = WorkingMemory()
    
    def _get_crop_attr(self, crop: Crop, attr_path: str) -> Any:
        """Get crop attribute from dotted path like 'crop.temp_lethal_min'"""
        parts = attr_path.split('.')
        if parts[0] == 'crop' and len(parts) > 1:
            return getattr(crop, parts[1], None)
        return None
    
    def _resolve_value(self, value: Any, crop: Crop) -> Any:
        """Resolve crop.xxx references and handle lists"""
        if isinstance(value, list):
            return [self._resolve_value(v, crop) for v in value]
        if isinstance(value, str) and value.startswith('crop.'):
            return self._get_crop_attr(crop, value)
        return value
    
    def is_rule_triggered(self, rule: Rule, crop: Crop) -> bool:
        """Check if all conditions are satisfied"""
        for condition in rule.conditions:
            fact_name = condition["fact"]
            
            # Check if condition references crop attributes
            if fact_name.startswith("crop."):
                fact_value = self._get_crop_attr(crop, fact_name)
            else:
                fact_value = self.working_memory.get_fact(fact_name)
            
            # Skip if fact is None and operator is not null check
            if fact_value is None and condition["operator"] not in ["is_null", "is_not_null"]:
                return False
            
            test_value = self._resolve_value(condition["value"], crop)
            
            # Special handling for 'in' operator with string values
            if condition["operator"] == "in" and isinstance(test_value, str):
                test_value = [v.strip() for v in test_value.split(',')] if test_value else []
            
            if not rule.evaluate_condition(fact_value, condition["operator"], test_value):
                return False
        
        return True
    
    def apply_rule(self, rule: Rule, crop: Crop) -> List[tuple]:
        """Apply rule and return new facts"""
        conclusion = rule.conclusion
        fact_name = conclusion["fact"]
        fact_value = conclusion["value"]
        
        # Create new dict to avoid mutating original rules
        if isinstance(fact_value, dict):
            resolved_value = {}
            for key, val in fact_value.items():
                resolved_value[key] = self._resolve_value(val, crop)
            fact_value = resolved_value
        else:
            fact_value = self._resolve_value(fact_value, crop)
        
        return [(fact_name, fact_value, rule.certainty)]
    
    def forward_chaining(self, initial_facts: Dict[str, Any], crop: Crop) -> WorkingMemory:
        """Run forward chaining inference"""
        self.working_memory = WorkingMemory()
        
        # Load initial facts
        for fact_name, fact_value in initial_facts.items():
            if fact_value is not None:
                self.working_memory.add_fact(fact_name, fact_value, 1.0, "user_input")
        
        # Add crop to memory
        self.working_memory.add_fact("current_crop", crop, 1.0, "system")
        
        rules_fired = set()
        
        for _ in range(50):  # Max iterations
            # Find triggered rules
            agenda = []
            for rule in self.kb.rules:
                if rule.rule_id not in rules_fired:
                    if self.is_rule_triggered(rule, crop):
                        agenda.append(rule)
            
            if not agenda:
                break
            
            # Select rule with highest priority and specificity
            agenda.sort(key=lambda r: (r.priority, r.specificity), reverse=True)
            selected = agenda[0]
            
            # Apply rule
            new_facts = self.apply_rule(selected, crop)
            for fact_name, fact_value, certainty in new_facts:
                self.working_memory.add_fact(fact_name, fact_value, certainty, selected.rule_id)
            
            rules_fired.add(selected.rule_id)
        
        return self.working_memory