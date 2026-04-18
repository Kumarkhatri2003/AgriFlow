from statistics import median
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import os


@dataclass
class Rule:
    """Expert system rule with conditions, conclusion, and metadata"""
    rule_id: str
    name: str
    conditions: List[Dict]
    conclusion: Dict
    certainty: float = 0.7
    priority: int = 1
    category: str = "soft"
    explanation: str = ""
    mitigation: Optional[str] = None
    
    def __post_init__(self):
        self.specificity = len(self.conditions)
    
    def evaluate_condition(self, fact_value: Any, operator: str, test_value: Any) -> bool:
        """Evaluate a single condition with full operator support"""
        # Handle null checks
        if operator == "is_not_null":
            return fact_value is not None
        if operator == "is_null":
            return fact_value is None
        
        if fact_value is None:
            return False
        
        # Convert to string for string comparisons
        if operator in ["eq", "neq", "contains"]:
            fact_value = str(fact_value)
            if not isinstance(test_value, list):
                test_value = str(test_value)
        
        # Convert to float for numeric comparisons
        if operator in ["lt", "lte", "gt", "gte", "between"]:
            try:
                fact_value = float(fact_value)
            except (TypeError, ValueError):
                pass
        
        if operator == "eq":
            return str(fact_value) == str(test_value)
        elif operator == "neq":
            return str(fact_value) != str(test_value)
        elif operator == "lt":
            try:
                return float(fact_value) < float(test_value)
            except (TypeError, ValueError):
                return False
        elif operator == "lte":
            try:
                return float(fact_value) <= float(test_value)
            except (TypeError, ValueError):
                return False
        elif operator == "gt":
            try:
                return float(fact_value) > float(test_value)
            except (TypeError, ValueError):
                return False
        elif operator == "gte":
            try:
                return float(fact_value) >= float(test_value)
            except (TypeError, ValueError):
                return False
        elif operator == "in":
            if isinstance(test_value, str):
                test_list = [v.strip() for v in test_value.split(',')]
            elif isinstance(test_value, list):
                test_list = test_value
            else:
                test_list = [str(test_value)]
            return str(fact_value) in [str(v) for v in test_list]
        elif operator == "contains":
            return str(test_value) in str(fact_value)
        elif operator == "between":
            try:
                low = float(test_value[0])
                high = float(test_value[1])
                fact_num = float(fact_value)
                return low <= fact_num <= high
            except (TypeError, ValueError):
                return False
        return False


@dataclass
class Crop:
    """Crop data from Django CropKnowledgeBase"""
    id: Any
    name_en: str
    name_np: str
    category: str
    
    # Temperature (°C)
    temp_min: float
    temp_max: float
    temp_optimal: float
    temp_lethal_min: float
    temp_lethal_max: float
    
    # Water
    water_requirement: str
    drought_tolerance: str
    water_logging_tolerance: str
    
    # Soil
    soil_ideal: str
    soil_acceptable: List[str]
    ph_ideal: float
    ph_min: float
    ph_max: float
    
    # NPK (kg/hectare)
    n_need_min: float
    n_need_max: float
    p_need_min: float
    p_need_max: float
    k_need_min: float
    k_need_max: float
    
    # Other
    region_suitable: List[str]
    best_season: str
    other_seasons: List[str]
    frost_sensitive: bool
    day_length_sensitive: bool = False
    day_length_type: Optional[str] = None
    growing_days: int = 100
    altitude_min: int = 0
    altitude_max: int = 3000
    
    labor_req: str = "medium"
    storage_life: str = "medium"
    

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id) if self.id else None,
            "name_en": self.name_en,
            "name_np": self.name_np,
            "category": self.category,
            "temp_min": self.temp_min,
            "temp_max": self.temp_max,
            "temp_optimal": self.temp_optimal,
            "n_need_min": self.n_need_min,
            "n_need_max": self.n_need_max,
            "p_need_min": self.p_need_min,
            "p_need_max": self.p_need_max,
            "k_need_min": self.k_need_min,
            "k_need_max": self.k_need_max,
            "best_season": self.best_season,
            "soil_ideal": self.soil_ideal,
            "ph_ideal": self.ph_ideal,
            "labor_req": self.labor_req,
            "storage_life": self.storage_life,
        }
    
    def get_npk_status(self, n: float, p: float, k: float) -> Dict:
        
        status = {
            "nitrogen": {"status": "Fits", "message": "", "suggestion": "", "score": 0},
            "phosphorus": {"status": "Fits", "message": "", "suggestion": "", "score": 0},
            "potassium": {"status": "Fits", "message": "", "suggestion": "", "score": 0},
            "total_score": 0
        }
        
        # ========== NITROGEN SCORING ==========
        if n is not None:
            if self.n_need_min <= n <= self.n_need_max:
                # Check if it's perfectly centered
                center = (self.n_need_min + self.n_need_max) / 2
                if abs(n - center) <= (self.n_need_max - self.n_need_min) * 0.2:
                    status["nitrogen"] = {
                        "status": "Perfect", 
                        "message": f"N: {n} kg/ha is perfect for this crop", 
                        "suggestion": "No action needed - maintain current nitrogen level",
                        "score": 15
                    }
                else:
                    status["nitrogen"] = {
                        "status": "Fits", 
                        "message": f"N: {n} kg/ha fits within crop need range ({self.n_need_min}-{self.n_need_max} kg/ha)", 
                        "suggestion": "Current nitrogen level is acceptable",
                        "score": 10
                    }
            elif n < self.n_need_min:
                deficit = self.n_need_min - n
                deficit_percent = (deficit / self.n_need_min) * 100
                if deficit_percent < 20:
                    status["nitrogen"] = {
                        "status": "Low", 
                        "message": f"N: {n} kg/ha is slightly low (needs {self.n_need_min}-{self.n_need_max} kg/ha)", 
                        "suggestion": "Add 25-30 kg/ha urea or apply well-decomposed compost",
                        "score": -5
                    }
                else:
                    status["nitrogen"] = {
                        "status": "Very Low", 
                        "message": f"N: {n} kg/ha is too low for this crop (needs {self.n_need_min}-{self.n_need_max} kg/ha)", 
                        "suggestion": "Apply 50-60 kg/ha urea or 4-5 tons/ha compost before planting",
                        "score": -15
                    }
            else:  # n > n_need_max
                excess = n - self.n_need_max
                excess_percent = (excess / self.n_need_max) * 100
                if excess_percent < 20:
                    status["nitrogen"] = {
                        "status": "High", 
                        "message": f"N: {n} kg/ha is slightly high (needs {self.n_need_min}-{self.n_need_max} kg/ha)", 
                        "suggestion": "Reduce nitrogen fertilizer by 30-40%. Consider planting a cover crop to absorb excess nitrogen.",
                        "score": -8
                    }
                else:
                    status["nitrogen"] = {
                        "status": "Very High", 
                        "message": f"N: {n} kg/ha is too high for this crop (needs only {self.n_need_max} kg/ha max)", 
                        "suggestion": "STOP adding nitrogen! Too much causes weak stems, pest problems, and delayed harvest. Plant deep-rooted crops to absorb excess.",
                        "score": -20
                    }
        
        # ========== PHOSPHORUS SCORING ==========
        if p is not None:
            if self.p_need_min <= p <= self.p_need_max:
                center = (self.p_need_min + self.p_need_max) / 2
                if abs(p - center) <= (self.p_need_max - self.p_need_min) * 0.2:
                    status["phosphorus"] = {
                        "status": "Perfect", 
                        "message": f"P: {p} kg/ha is perfect for this crop", 
                        "suggestion": "No action needed - maintain current phosphorus level",
                        "score": 12
                    }
                else:
                    status["phosphorus"] = {
                        "status": "Fits", 
                        "message": f"P: {p} kg/ha fits within crop need range ({self.p_need_min}-{self.p_need_max} kg/ha)", 
                        "suggestion": "Current phosphorus level is acceptable",
                        "score": 8
                    }
            elif p < self.p_need_min:
                deficit = self.p_need_min - p
                deficit_percent = (deficit / self.p_need_min) * 100
                if deficit_percent < 20:
                    status["phosphorus"] = {
                        "status": "Low", 
                        "message": f"P: {p} kg/ha is slightly low (needs {self.p_need_min}-{self.p_need_max} kg/ha)", 
                        "suggestion": "Add 15-20 kg/ha DAP or 2-3 tons/ha compost",
                        "score": -4
                    }
                else:
                    status["phosphorus"] = {
                        "status": "Very Low", 
                        "message": f"P: {p} kg/ha is too low for this crop (needs {self.p_need_min}-{self.p_need_max} kg/ha)", 
                        "suggestion": "Apply 30-40 kg/ha DAP or 4-5 tons/ha well-decomposed manure",
                        "score": -12
                    }
            else:  # p > p_need_max
                excess = p - self.p_need_max
                excess_percent = (excess / self.p_need_max) * 100
                if excess_percent < 20:
                    status["phosphorus"] = {
                        "status": "High", 
                        "message": f"P: {p} kg/ha is slightly high (needs {self.p_need_min}-{self.p_need_max} kg/ha)", 
                        "suggestion": "Reduce phosphorus fertilizer. Consider adding zinc to prevent deficiency caused by high P.",
                        "score": -6
                    }
                else:
                    status["phosphorus"] = {
                        "status": "Very High", 
                        "message": f"P: {p} kg/ha is too high for this crop (needs only {self.p_need_max} kg/ha max)", 
                        "suggestion": "STOP adding phosphorus! Excess P blocks zinc and iron uptake. Apply zinc sulfate if deficiency appears.",
                        "score": -18
                    }
        
        # ========== POTASSIUM SCORING ==========
        if k is not None:
            if self.k_need_min <= k <= self.k_need_max:
                center = (self.k_need_min + self.k_need_max) / 2
                if abs(k - center) <= (self.k_need_max - self.k_need_min) * 0.2:
                    status["potassium"] = {
                        "status": "Perfect", 
                        "message": f"K: {k} kg/ha is perfect for this crop", 
                        "suggestion": "No action needed - maintain current potassium level",
                        "score": 10
                    }
                else:
                    status["potassium"] = {
                        "status": "Fits", 
                        "message": f"K: {k} kg/ha fits within crop need range ({self.k_need_min}-{self.k_need_max} kg/ha)", 
                        "suggestion": "Current potassium level is acceptable",
                        "score": 7
                    }
            elif k < self.k_need_min:
                deficit = self.k_need_min - k
                deficit_percent = (deficit / self.k_need_min) * 100
                if deficit_percent < 20:
                    status["potassium"] = {
                        "status": "Low", 
                        "message": f"K: {k} kg/ha is slightly low (needs {self.k_need_min}-{self.k_need_max} kg/ha)", 
                        "suggestion": "Add 15-20 kg/ha MOP or apply wood ash",
                        "score": -4
                    }
                else:
                    status["potassium"] = {
                        "status": "Very Low", 
                        "message": f"K: {k} kg/ha is too low for this crop (needs {self.k_need_min}-{self.k_need_max} kg/ha)", 
                        "suggestion": "Apply 30-40 kg/ha MOP or 2-3 tons/ha compost",
                        "score": -12
                    }
            else:  # k > k_need_max
                excess = k - self.k_need_max
                excess_percent = (excess / self.k_need_max) * 100
                if excess_percent < 20:
                    status["potassium"] = {
                        "status": "High", 
                        "message": f"K: {k} kg/ha is slightly high (needs {self.k_need_min}-{self.k_need_max} kg/ha)", 
                        "suggestion": "Reduce potassium fertilizer. Add magnesium to prevent deficiency.",
                        "score": -5
                    }
                else:
                    status["potassium"] = {
                        "status": "Very High", 
                        "message": f"K: {k} kg/ha is too high for this crop (needs only {self.k_need_max} kg/ha max)", 
                        "suggestion": "STOP adding potassium! Excess K blocks magnesium and calcium uptake. Apply Epsom salt (magnesium sulfate) if deficiency appears.",
                        "score": -15
                    }
        
        # Calculate total NPK score (can be negative!)
        total = 0
        for key in ["nitrogen", "phosphorus", "potassium"]:
            total += status[key]["score"]
        status["total_score"] = total
        
        return status


class KnowledgeBase:
    """Central knowledge repository"""
    
    def __init__(self):
        self.crops: Dict[Any, Crop] = {}
        self.rules: List[Rule] = []
    
    def load_crops(self, crops_data: List[Dict]):
        """Load crop data from dictionary list"""
        for crop_dict in crops_data:
            crop = Crop(**crop_dict)
            self.crops[crop.id] = crop
    
    def load_rules_from_list(self, rules_list: List[Dict]):
        """Load rules from list of dicts"""
        for rule_dict in rules_list:
            rule = Rule(**rule_dict)
            self.rules.append(rule)
    
    def load_rules_from_json(self, json_path: str):
        """Load rules from JSON file"""
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            self.load_rules_from_list(rules_data)
    
    def get_crop(self, crop_id) -> Optional[Crop]:
        return self.crops.get(crop_id)
    
    def get_all_crops(self) -> List[Crop]:
        return list(self.crops.values())