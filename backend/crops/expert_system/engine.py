"""
AgriFlow Expert System - Main Orchestration
Hybrid Rule-Based Crop Recommendation Engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from functools import lru_cache

from .knowledge_base import KnowledgeBase, Crop
from .inference_engine import InferenceEngine
from .uncertainty import UncertaintyManager
from .explanation import ExplanationFacility, Explanation


@dataclass
class RecommendationConfig:
    """Configuration for recommendation engine"""
    min_confidence: float = 0.50
    max_recommendations: int = 10
    enable_early_pruning: bool = True
    enable_caching: bool = True
    debug_mode: bool = False


@dataclass
class Recommendation:
    """Final recommendation output"""
    crop_id: Any
    crop_name: str
    crop_name_np: str
    confidence: float
    feasibility: str
    explanation: Explanation
    actionable_advice: List[str]
    factor_scores: Dict[str, float]
    npk_status: Dict
    
    def to_dict(self) -> Dict:
        return {
            "crop_id": str(self.crop_id) if self.crop_id else None,
            "crop_name": self.crop_name,
            "crop_name_np": self.crop_name_np,
            "confidence": round(self.confidence * 100, 1),
            "feasibility": self.feasibility,
            "explanation": self.explanation.to_dict(),
            "actionable_advice": self.actionable_advice,
            "factor_scores": self.factor_scores,
            "npk_status": self.npk_status
        }


class AgriFlowExpertSystem:
    """Main expert system for crop recommendation"""
    
    # Soil type normalization map
    SOIL_MAP = {
        'loamy': 'Loamy',
        'clay': 'Clay', 
        'sandy': 'Sandy',
        'silty': 'Silty',
        'clay_loam': 'Clay Loam',
        'sandy_loam': 'Sandy Loam',
        'loam': 'Loam',
        'clay/loam': 'Clay/Loam',
    }
    
    def __init__(self, config: RecommendationConfig = None):
        self.config = config or RecommendationConfig()
        self.kb = KnowledgeBase()
        self.inference = None
        self.explainer = ExplanationFacility()
        self.is_initialized = False
        self._cache = {}
    
    def initialize(self, crops_queryset) -> int:
        """Initialize from Django queryset"""
        crops_data = []
        
        for db_crop in crops_queryset:
            # Parse comma-separated fields
            other_seasons = [s.strip() for s in db_crop.other_seasons.split(',') if s.strip()] if db_crop.other_seasons else []
            soil_acceptable = [s.strip() for s in db_crop.soil_other.split(',') if s.strip()] if db_crop.soil_other else []
            region_suitable = [r.strip().lower() for r in db_crop.region_suitable.split(',') if r.strip()] if db_crop.region_suitable else []
            
            # Keep frost_sensitive as string
            frost_sensitive = db_crop.frost_sensitive
            
            crop_dict = {
                "id": db_crop.id,
                "name_en": db_crop.name_en,
                "name_np": db_crop.name_np or db_crop.name_en,
                "category": db_crop.category,
                "temp_min": db_crop.temp_min,
                "temp_max": db_crop.temp_max,
                "temp_optimal": db_crop.temp_ideal,
                "temp_lethal_min": db_crop.temp_min - 5,
                "temp_lethal_max": db_crop.temp_max + 5,
                "water_requirement": db_crop.water_req,
                "drought_tolerance": db_crop.drought_tolerance,
                "water_logging_tolerance": db_crop.water_logging_tolerance,
                "soil_ideal": db_crop.soil_ideal,
                "soil_acceptable": soil_acceptable,
                "ph_ideal": db_crop.ph_ideal,
                "ph_min": db_crop.ph_min,
                "ph_max": db_crop.ph_max,
                "n_need_min": max(20, db_crop.n_need * 0.6),
                "n_need_max": db_crop.n_need * 1.4,
                "p_need_min": max(10, db_crop.p_need * 0.6),
                "p_need_max": db_crop.p_need * 1.4,
                "k_need_min": max(10, db_crop.k_need * 0.6),
                "k_need_max": db_crop.k_need * 1.4,
                "region_suitable": region_suitable,
                "best_season": db_crop.best_season,
                "other_seasons": other_seasons,
                "frost_sensitive": frost_sensitive,
                "day_length_sensitive": db_crop.day_length_sensitive,
                "day_length_type": db_crop.day_length_type,
                "growing_days": db_crop.growing_days,
                "altitude_min": db_crop.altitude_min,
                "altitude_max": db_crop.altitude_max,
                "labor_req": db_crop.labor_req,
                "storage_life": db_crop.storage_life,
            }
            crops_data.append(crop_dict)
        
        self.kb.load_crops(crops_data)
        
        # Load rules from JSON
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'rules.json')
        if os.path.exists(json_path):
            self.kb.load_rules_from_json(json_path)
        else:
            print(f"Warning: Rules file not found at {json_path}")
        
        self.inference = InferenceEngine(self.kb)
        self.is_initialized = True
        
        return len(crops_data)
    
    def _normalize_soil_type(self, soil_type: str) -> str:
        """Normalize soil type from frontend to match database format"""
        if not soil_type:
            return soil_type
        return self.SOIL_MAP.get(soil_type.lower(), soil_type)
    
    def _get_current_season(self) -> str:
        """Get current season based on Nepali context"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8, 9]:
            return "monsoon"
        elif month in [10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def _get_default_temperature(self, region: str, season: str) -> float:
        """Get default temperature based on region and season"""
        temp_defaults = {
            "terai": {"spring": 23.5, "monsoon": 29.5, "autumn": 24, "winter": 14.5},
            "mid-hill": {"spring": 17.5, "monsoon": 23, "autumn": 18, "winter": 10},
            "hill": {"spring": 12.5, "monsoon": 17, "autumn": 12, "winter": 5},
            "mountain": {"spring": 5, "monsoon": 12, "autumn": 2.5, "winter": -5}
        }
        return temp_defaults.get(region, temp_defaults["terai"]).get(season, 20)
    
    def validate_farmer_data(self, farmer_data: Dict) -> Dict:
        """Validate and sanitize farmer inputs"""
        validated = {}
        
        # Valid regions
        valid_regions = ['terai', 'mid-hill', 'hill', 'mountain']
        region = farmer_data.get('region', 'terai')
        validated['region'] = region if region in valid_regions else 'terai'
        
        # Valid soil types
        valid_soils = ['clay', 'loamy', 'sandy', 'silty', 'clay_loam']
        soil = farmer_data.get('soil_type', 'loamy')
        validated['soil_type'] = soil if soil in valid_soils else 'loamy'
        
        # Valid water sources
        valid_water = ['rainfed_only', 'canal', 'well', 'river', 'drip_irrigation']
        water = farmer_data.get('water_source', 'rainfed_only')
        validated['water_source'] = water if water in valid_water else 'rainfed_only'
        
        # Valid farming goals
        valid_goals = ['profit', 'food_security', 'mixed', 'subsistence']
        goal = farmer_data.get('farming_goal', 'mixed')
        validated['farming_goal'] = goal if goal in valid_goals else 'mixed'
        
        # Valid labor availability
        valid_labor = ['low', 'medium', 'high']
        labor = farmer_data.get('labor_availability', 'medium')
        validated['labor_availability'] = labor if labor in valid_labor else 'medium'
        
        # Valid market distance
        valid_market = ['near', 'medium', 'far']
        market = farmer_data.get('market_distance', 'near')
        validated['market_distance'] = market if market in valid_market else 'near'
        
        # Validate NPK ranges
        for nutrient in ['n', 'p', 'k']:
            value = farmer_data.get(nutrient)
            if value is not None:
                try:
                    val = float(value)
                    validated[nutrient] = max(0, min(500, val))
                except (TypeError, ValueError):
                    validated[nutrient] = None
            else:
                validated[nutrient] = None
        
        # Validate pH
        ph = farmer_data.get('ph')
        if ph is not None:
            try:
                validated['ph'] = max(0, min(14, float(ph)))
            except (TypeError, ValueError):
                validated['ph'] = None
        else:
            validated['ph'] = None
        
        # Temperature
        if 'temperature' in farmer_data and farmer_data['temperature'] is not None:
            try:
                validated['temperature'] = float(farmer_data['temperature'])
            except (TypeError, ValueError):
                validated['temperature'] = None
        else:
            validated['temperature'] = None
        
        # Frost risk
        if 'frost_risk' in farmer_data:
            frost_val = farmer_data['frost_risk']
            if isinstance(frost_val, bool):
                validated['frost_risk'] = frost_val
            elif isinstance(frost_val, str):
                validated['frost_risk'] = frost_val.lower() == 'yes'
            else:
                validated['frost_risk'] = False
        else:
            validated['frost_risk'] = False
        
        # Drought risk
        if 'drought_risk' in farmer_data:
            validated['drought_risk'] = farmer_data['drought_risk']
        else:
            validated['drought_risk'] = 'medium'
        
        validated['season'] = farmer_data.get('season') or self._get_current_season()
        
        return validated
    
    def _score_npk(self, crop: Crop, n: float, p: float, k: float) -> Dict:
        """Calculate NPK match score and status"""
        return crop.get_npk_status(n, p, k)
    
    def _should_prune_crop(self, crop: Crop, region: str, season: str = None, goal: str = "mixed", 
                           labor: str = "medium", market: str = "near", water_source: str = "rainfed_only") -> bool:
        """
        Early pruning for definitely impossible crops
        Returns True if crop should be pruned (not evaluated)
        """
        # HARD CONSTRAINT 1: Region mismatch - IMMEDIATE REJECT
        if region not in crop.region_suitable:
            return True
        
        # ========== GOAL-BASED HARD CONSTRAINTS ==========
        
        # FOOD SECURITY GOAL - Focus on staple foods for survival
        if goal == "food_security":
            # Reject cash crops (can't eat them)
            if crop.category == "cash_crop":
                return True
            # Reject very long growing days (>6 months)
            if crop.growing_days > 180:
                return True
            # Reject very short storage life (can't store for lean season)
            if crop.storage_life == "very_short":
                return True
            # Reject high labor crops with low labor availability
            if labor == "low" and crop.labor_req == "high":
                return True
            # Water constraint: only reject if rainfed AND high requirement
            if water_source == "rainfed_only" and crop.water_requirement == "high":
                return True
        
        # SUBSISTENCE GOAL - Pure survival farming (most restrictive)
        elif goal == "subsistence":
            # Reject cash crops (can't eat them)
            if crop.category == "cash_crop":
                return True
            # Reject oilseeds (not essential for survival, optional)
            if crop.category == "oilseed":
                return True
            # Reject very long growing days (>5 months - too long to wait for harvest)
            if crop.growing_days > 150:
                return True
            # Reject very short storage life (cannot store for lean season)
            if crop.storage_life == "very_short":
                return True
            # Reject high labor crops with low labor availability
            if labor == "low" and crop.labor_req == "high":
                return True
            # Only essential crops: cereals, pulses, tubers, vegetables
            if crop.category not in ["cereal", "pulse", "tuber", "vegetable"]:
                return True
            # WATER CONSTRAINT: Only reject if rainfed ONLY AND high requirement
            # If farmer has river/canal/well/drip irrigation, high water crops are acceptable
            if water_source == "rainfed_only" and crop.water_requirement == "high":
                return True
        
        # PROFIT GOAL - Focus on market value and return on investment
        elif goal == "profit":
            # Reject very long growing days (>10 months, slow ROI)
            if crop.growing_days > 300:
                return True
            # Reject very short storage life with far market (spoilage risk)
            if market == "far" and crop.storage_life == "very_short":
                return True
            # Water constraint: high water requirement with rainfed reduces profit
            if water_source == "rainfed_only" and crop.water_requirement == "high":
                # Don't reject, but will have lower score
                pass
        
        return False
    
    def recommend(self, farmer_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate crop recommendations with HARSH scoring"""
        if not self.is_initialized:
            return []
        
        # Validate input data
        farmer_data = self.validate_farmer_data(farmer_data)
        
        # Prepare initial facts
        season = farmer_data.get("season", self._get_current_season())
        region = farmer_data.get("region", "terai")
        
        # Handle temperature
        temperature = farmer_data.get("temperature")
        if temperature is None:
            temperature = self._get_default_temperature(region, season)
        
        # Normalize soil type
        raw_soil = farmer_data.get("soil_type", "loamy")
        normalized_soil = self._normalize_soil_type(raw_soil)
        
        # Extract values
        n_value = farmer_data.get("n")
        p_value = farmer_data.get("p")
        k_value = farmer_data.get("k")
        ph_value = farmer_data.get("ph")
        frost_risk = farmer_data.get("frost_risk", False)
        drought_risk = farmer_data.get("drought_risk", "medium")
        labor = farmer_data.get("labor_availability", "medium")
        market = farmer_data.get("market_distance", "near")
        goal = farmer_data.get("farming_goal", "mixed")
        water_source = farmer_data.get("water_source", "rainfed_only")
        
        initial_facts = {
            "region": region,
            "soil_type": normalized_soil,
            "water_source": water_source,
            "season": season,
            "temperature": temperature,
            "frost_risk": frost_risk,
            "ph": ph_value,
            "n": n_value,
            "p": p_value,
            "k": k_value,
            "drought_risk": drought_risk,
        }
        
        recommendations = []
        
        # Get all crops
        all_crops = self.kb.get_all_crops()
        
        # Apply early pruning with goal, labor, market, and water_source parameters
        if self.config.enable_early_pruning:
            viable_crops = [
                crop for crop in all_crops 
                if not self._should_prune_crop(crop, region, season, goal, labor, market, water_source)
            ]
        else:
            viable_crops = all_crops
        
        if self.config.debug_mode:
            pruned_count = len(all_crops) - len(viable_crops)
            print(f"[DEBUG] Total crops: {len(all_crops)}, Pruned: {pruned_count}, Viable: {len(viable_crops)}")
            print(f"[DEBUG] Goal: {goal}, Labor: {labor}, Market: {market}, Water: {water_source}")
        
        for crop in viable_crops:
            # Run inference for all rules
            working_memory = self.inference.forward_chaining(initial_facts, crop)
            
            # ========== EXTRACT RULE ADJUSTMENTS ==========
            rule_adjustment = 0
            adjustment_fact = working_memory.get_fact("crop_score_adjustment")
            if adjustment_fact and isinstance(adjustment_fact, dict):
                rule_adjustment = adjustment_fact.get("adjustment", 0)
            
            # ========== COMBINE CERTAINTY FACTORS ==========
            rule_certainties = [
                trace["certainty"] 
                for trace in working_memory.rule_trace 
                if "certainty" in trace
            ]
            combined_cf = UncertaintyManager.combine_multiple(rule_certainties) if rule_certainties else 1.0
            
            # ========== HARSH SCORING WITH PERFECT MATCH CAP ==========
            total_score = 0.0
            penalties = 0
            
            # 1. SEASON (30 points) - WITH PENALTY FOR WRONG SEASON
            if season == crop.best_season:
                season_score = 30
            elif season in crop.other_seasons:
                season_score = 15
            else:
                season_score = 0
                penalties += 10
            total_score += season_score
            
            # 2. REGION (20 points)
            if region in crop.region_suitable:
                region_score = 20
            else:
                region_score = 0
            total_score += region_score
            
            # 3. SOIL (15 points) - WITH NORMALIZATION
            crop_soil_ideal = self._normalize_soil_type(crop.soil_ideal)
            crop_soil_acceptable = [self._normalize_soil_type(s) for s in crop.soil_acceptable]
            
            if normalized_soil == crop_soil_ideal:
                soil_score = 15
            elif normalized_soil in crop_soil_acceptable:
                soil_score = 8
            else:
                soil_score = 0
                penalties += 8
            total_score += soil_score
            
            # 4. TEMPERATURE (15 points) - MORE STRICT
            if crop.temp_min <= temperature <= crop.temp_max:
                optimal_center = (crop.temp_min + crop.temp_max) / 2
                deviation = abs(temperature - optimal_center)
                range_width = (crop.temp_max - crop.temp_min) / 2
                
                if range_width > 0:
                    percentage = 1 - (deviation / range_width)
                    if percentage >= 0.9:
                        temp_score = 15
                    elif percentage >= 0.7:
                        temp_score = 10
                    elif percentage >= 0.5:
                        temp_score = 5
                    elif percentage >= 0.3:
                        temp_score = 2
                    else:
                        temp_score = 0
                else:
                    temp_score = 15 if temperature == crop.temp_min else 5
            else:
                temp_score = 0
                penalties += 15
            total_score += temp_score
            
            # 5. WATER (10 points) - MORE STRICT WITH DROUGHT PENALTY
            if water_source != "rainfed_only":
                water_score = 10
            else:
                if crop.drought_tolerance == "high":
                    water_score = 6
                elif crop.drought_tolerance == "medium":
                    water_score = 3
                else:
                    water_score = 0
                
                # Drought risk penalty
                if drought_risk == "high" and crop.drought_tolerance != "high":
                    penalties += 10
                elif drought_risk == "high" and crop.drought_tolerance == "medium":
                    penalties += 5
                elif drought_risk == "low" and crop.drought_tolerance == "high":
                    total_score += 3
            total_score += water_score
            
            # 6. pH (10 points)
            if ph_value is not None:
                if crop.ph_min <= ph_value <= crop.ph_max:
                    if abs(ph_value - crop.ph_ideal) <= 0.3:
                        ph_score = 10
                    elif abs(ph_value - crop.ph_ideal) <= 0.7:
                        ph_score = 7
                    else:
                        ph_score = 5
                else:
                    ph_score = 0
                    penalties += 5
            else:
                ph_score = 3
            total_score += ph_score
            
            # 7. FROST (Penalty)
            if frost_risk:
                if crop.frost_sensitive == 'yes':
                    total_score -= 30
                elif crop.frost_sensitive == 'tolerant':
                    total_score -= 10
            
            # 8. NPK (Bonus/Penalty)
            npk_bonus = 0
            npk_result = {}
            if n_value is not None and p_value is not None and k_value is not None:
                npk_result = self._score_npk(crop, n_value, p_value, k_value)
                npk_score = npk_result.get("total_score", 0)
                npk_bonus = min(10, max(-10, npk_score / 10))
                total_score += npk_bonus
            
            # 9. LABOR (Penalty)
            if labor == "low" and crop.labor_req == "high":
                total_score -= 15
            elif labor == "low" and crop.labor_req == "medium":
                total_score -= 5
            
            # 10. MARKET (Penalty)
            if market == "far" and crop.storage_life in ["very_short", "short"]:
                total_score -= 12
            elif market == "far" and crop.storage_life == "medium":
                total_score -= 5
            
            # 11. GOAL BONUS & ADJUSTMENTS
            if goal == "profit":
                # Profit goal: prioritize cash crops and oilseeds
                if crop.category == "cash_crop":
                    total_score += 10
                elif crop.category == "oilseed":
                    total_score += 5
                    
            elif goal == "food_security":
                # Food security goal: prioritize staples, accept vegetables
                if crop.category in ["cereal", "pulse"]:
                    total_score += 10
                elif crop.category in ["vegetable", "tuber"]:
                    total_score += 6
                elif crop.category == "oilseed":
                    total_score += 2
                    
            elif goal == "subsistence":
                # Subsistence goal: maximum priority for essential crops
                if crop.category in ["cereal", "pulse"]:
                    total_score += 15
                elif crop.category in ["tuber", "vegetable"]:
                    total_score += 10
                    
            elif goal == "mixed":
                total_score += 3
            
            # 12. Apply penalties
            total_score -= penalties
            
            # 13. Apply rule adjustments (capped)
            max_rule_adjustment = 15
            min_rule_adjustment = -25
            capped_rule_adjustment = max(min_rule_adjustment, min(max_rule_adjustment, rule_adjustment))
            total_score += capped_rule_adjustment
            
            # ========== PERFECT MATCH CAP - EVEN BEST CROPS DON'T GET 100% ==========
            # Maximum realistic score for perfectly matched crop is 92%
            if total_score > 92:
                excess = total_score - 92
                total_score = 92 + (excess * 0.2)  # Only 20% of excess above 92
            elif total_score > 85:
                excess = total_score - 85
                total_score = 85 + (excess * 0.5)  # Only 50% of excess above 85
            
            # Cap at 100, minimum 0 (but realistically won't reach 100)
            total_score = max(0, min(100, total_score))
            
            # Calculate base confidence
            base_confidence = total_score / 100
            
            # Apply certainty factor to get final confidence
            final_confidence = base_confidence * combined_cf
            final_confidence = max(0.0, min(0.95, final_confidence))  # Hard cap at 95% max
            
            # ========== REJECT CROPS BELOW MIN CONFIDENCE ==========
            if final_confidence < self.config.min_confidence:
                continue
            
            # Check if crop is possible (hard constraints from inference)
            crop_possible = working_memory.get_fact("crop_possible")
            if crop_possible is False:
                continue
            
            # Determine feasibility
            if final_confidence >= 0.75:
                feasibility = "high"
            elif final_confidence >= 0.60:
                feasibility = "medium"
            else:
                feasibility = "low"
            
            # Generate NPK result for explanation
            if n_value is not None or p_value is not None or k_value is not None:
                npk_result = self._score_npk(crop, n_value, p_value, k_value)
            else:
                npk_result = {
                    "nitrogen": {"status": "Unknown", "message": "No soil test data", "suggestion": "Conduct soil test", "score": 0},
                    "phosphorus": {"status": "Unknown", "message": "No soil test data", "suggestion": "Conduct soil test", "score": 0},
                    "potassium": {"status": "Unknown", "message": "No soil test data", "suggestion": "Conduct soil test", "score": 0},
                    "total_score": 0
                }
            
            # Generate explanation
            crop_dict = crop.to_dict()
            explanation = self.explainer.explain_crop(
                crop.name_en,
                crop_dict,
                working_memory,
                final_confidence,
                npk_status=npk_result
            )
            
            # Store factor scores
            factor_scores = {
                "total": total_score,
                "season": season_score,
                "region": region_score,
                "soil": soil_score,
                "temperature": temp_score,
                "water": water_score,
                "ph": ph_score,
                "npk_bonus": npk_bonus,
                "rule_adjustment": capped_rule_adjustment,
                "certainty_factor": combined_cf,
                "penalties": penalties,
            }
            
            recommendations.append(Recommendation(
                crop_id=crop.id,
                crop_name=crop.name_en,
                crop_name_np=crop.name_np,
                confidence=final_confidence,
                feasibility=feasibility,
                explanation=explanation,
                actionable_advice=explanation.actionable_advice,
                factor_scores=factor_scores,
                npk_status=npk_result
            ))
        
        # Sort and limit
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        if self.config.max_recommendations > 0:
            recommendations = recommendations[:self.config.max_recommendations]
        
        return recommendations


# Singleton instance
_expert_system = None


def get_expert_system(config: RecommendationConfig = None):
    """Get or create expert system singleton"""
    global _expert_system
    if _expert_system is None:
        _expert_system = AgriFlowExpertSystem(config)
    return _expert_system


def get_recommendations(crops_queryset, farmer_data: Dict, config: RecommendationConfig = None) -> Dict:
    """Wrapper function for use in views"""
    es = get_expert_system(config)
    
    if not es.is_initialized:
        es.initialize(crops_queryset)
    
    recommendations = es.recommend(farmer_data)
    
    min_conf = config.min_confidence if config else 0.50
    feasible = [r for r in recommendations if r.confidence >= min_conf]
    
    summary = {
        "total_evaluated": len(recommendations),
        "possible_count": len(feasible),
        "high_feasibility": len([r for r in feasible if r.feasibility == "high"]),
        "medium_feasibility": len([r for r in feasible if r.feasibility == "medium"]),
        "low_feasibility": len([r for r in feasible if r.feasibility == "low"]),
    }
    
    if feasible:
        summary["best_crop"] = feasible[0].crop_name
        summary["best_confidence"] = round(feasible[0].confidence * 100, 1)
        summary["best_crop_npk"] = feasible[0].npk_status
    
    return {
        "success": True,
        "summary": summary,
        "recommendations": [r.to_dict() for r in feasible[:10]],
        "explanation_available": True
    }