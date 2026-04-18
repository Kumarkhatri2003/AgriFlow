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
        if fact_name in self.facts:
            # Handle adjustments to existing scores
            if isinstance(value, dict) and "adjustment" in value:
                if isinstance(self.facts[fact_name], dict):
                    self.facts[fact_name]["adjustment"] = self.facts[fact_name].get("adjustment", 0) + value["adjustment"]
                else:
                    self.facts[fact_name] = value
            else:
                self.facts[fact_name] = value
            self.certainties[fact_name] = max(certainty, self.certainties.get(fact_name, 0))
        else:
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
        return self.facts.get(fact_name)
    
    def get_certainty(self, fact_name: str) -> float:
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
        """Resolve crop.xxx references"""
        if isinstance(value, str) and value.startswith('crop.'):
            return self._get_crop_attr(crop, value)
        return value
    
    def is_rule_triggered(self, rule: Rule, crop: Crop) -> bool:
        """Check if all conditions are satisfied"""
        # Iterate over the rule's conditions (NOT Rule.conditions)
        for condition in rule.conditions:
            fact_value = self.working_memory.get_fact(condition["fact"])
            
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
        
        # Resolve crop references in the conclusion value
        if isinstance(fact_value, dict):
            for key, val in fact_value.items():
                fact_value[key] = self._resolve_value(val, crop)
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
            
            # Select rule with highest priority
            agenda.sort(key=lambda r: (r.priority, r.specificity), reverse=True)
            selected = agenda[0]
            
            # Apply rule
            new_facts = self.apply_rule(selected, crop)
            for fact_name, fact_value, certainty in new_facts:
                self.working_memory.add_fact(fact_name, fact_value, certainty, selected.rule_id)
            
            rules_fired.add(selected.rule_id)
        
        return self.working_memory