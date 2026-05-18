"""
AgriFlow Expert System - Main Orchestration
Hybrid Rule-Based Crop Recommendation Engine
"""

from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

from .knowledge_base import KnowledgeBase, Crop
from .inference_engine import InferenceEngine
from .uncertainty import UncertaintyManager
from .explanation import ExplanationFacility, Explanation


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
    
    def __init__(self):
        self.kb = KnowledgeBase()
        self.inference = None
        self.explainer = ExplanationFacility()
        self.is_initialized = False
    
    def initialize(self, crops_queryset):
        """Initialize from Django queryset"""
        crops_data = []
        
        for db_crop in crops_queryset:
            # Parse comma-separated fields
            other_seasons = [s.strip() for s in db_crop.other_seasons.split(',') if s.strip()] if db_crop.other_seasons else []
            soil_acceptable = [s.strip() for s in db_crop.soil_other.split(',') if s.strip()] if db_crop.soil_other else []
            region_suitable = [r.strip() for r in db_crop.region_suitable.split(',') if r.strip()] if db_crop.region_suitable else []
            
            # Keep frost_sensitive as string (not boolean)
            frost_sensitive = db_crop.frost_sensitive  # 'yes', 'no', or 'tolerant'
            
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
                "water_logging_tolerance": "medium",
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
                "frost_sensitive": frost_sensitive,  # String: 'yes', 'no', 'tolerant'
                "day_length_sensitive": False,
                "day_length_type": None,
                "growing_days": 100,
                "altitude_min": 0,
                "altitude_max": 3000,
                "labor_req": db_crop.labor_req,
                "storage_life": db_crop.storage_life,
            }
            crops_data.append(crop_dict)
        
        self.kb.load_crops(crops_data)
        
        # Load rules from JSON
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'rules.json')
        self.kb.load_rules_from_json(json_path)
        
        self.inference = InferenceEngine(self.kb)
        self.is_initialized = True
        
        return len(crops_data)
    
    def _get_current_season(self) -> str:
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
        temp_defaults = {
            "terai": {"spring": 23.5, "monsoon": 29.5, "autumn": 24, "winter": 14.5},
            "mid-hill": {"spring": 17.5, "monsoon": 23, "autumn": 18, "winter": 10},
            "hill": {"spring": 12.5, "monsoon": 17, "autumn": 12, "winter": 5},
            "mountain": {"spring": 5, "monsoon": 12, "autumn": 2.5, "winter": -5}
        }
        return temp_defaults.get(region, temp_defaults["terai"]).get(season, 20)
    
    def _score_npk(self, crop: Crop, n: float, p: float, k: float) -> Dict:
        """Calculate NPK match score and status"""
        return crop.get_npk_status(n, p, k)
    
    def recommend(self, farmer_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate crop recommendations with HARSH scoring - Only 50%+ crops survive"""
        if not self.is_initialized:
            return []
        
        # Prepare initial facts
        season = farmer_data.get("season")
        if not season:
            season = self._get_current_season()
        
        region = farmer_data.get("region", "terai")
        temperature = farmer_data.get("temperature_override")
        if not temperature:
            temperature = self._get_default_temperature(region, season)
        
        # Extract NPK values
        n_value = farmer_data.get("n")
        p_value = farmer_data.get("p")
        k_value = farmer_data.get("k")
        
        initial_facts = {
            "region": region,
            "soil_type": farmer_data.get("soil_type", "loamy"),
            "water_source": farmer_data.get("water_source", "rainfed_only"),
            "season": season,
            "temperature": temperature,
            "frost_risk": farmer_data.get("elevation_risk", False),
            "ph": farmer_data.get("ph"),
            "n": n_value,
            "p": p_value,
            "k": k_value,
        }
        
        recommendations = []
        
        for crop in self.kb.get_all_crops():
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
            
            # ========== HARSH SCORING ==========
            total_score = 0.0
            
            # 1. SEASON (30 points)
            if season == crop.best_season:
                season_score = 30
            elif season in crop.other_seasons:
                season_score = 15
            else:
                season_score = 0
            total_score += season_score
            
            # 2. REGION (20 points)
            if region in crop.region_suitable:
                region_score = 20
            else:
                region_score = 0
            total_score += region_score
            
            # 3. SOIL (15 points)
            soil_type = farmer_data.get("soil_type", "loamy")
            if soil_type == crop.soil_ideal:
                soil_score = 15
            elif soil_type in crop.soil_acceptable:
                soil_score = 8
            else:
                soil_score = 0
            total_score += soil_score
            
            # 4. TEMPERATURE (15 points)
            if crop.temp_min <= temperature <= crop.temp_max:
                optimal_center = (crop.temp_min + crop.temp_max) / 2
                deviation = abs(temperature - optimal_center)
                range_width = (crop.temp_max - crop.temp_min) / 2
                
                if range_width > 0:
                    percentage = 1 - (deviation / range_width)
                    if percentage >= 0.8:
                        temp_score = 15
                    elif percentage >= 0.6:
                        temp_score = 10
                    elif percentage >= 0.4:
                        temp_score = 5
                    else:
                        temp_score = 2
                else:
                    temp_score = 15 if temperature == crop.temp_min else 5
            else:
                temp_score = 0
            total_score += temp_score
            
            # 5. WATER (10 points)
            water_source = farmer_data.get("water_source", "rainfed_only")
            if water_source != "rainfed_only":
                water_score = 10
            else:
                if crop.drought_tolerance == "high":
                    water_score = 8
                elif crop.drought_tolerance == "medium":
                    water_score = 4
                else:
                    water_score = 0
            total_score += water_score
            
            # 6. pH (10 points)
            ph_value = farmer_data.get("ph")
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
            else:
                ph_score = 5  # Default when no soil test
            total_score += ph_score
            
            # 7. FROST (PENALTY) - Now works correctly with string values
            frost_risk = farmer_data.get("elevation_risk", False)
            if frost_risk:
                if crop.frost_sensitive == 'yes':
                    total_score -= 30
                elif crop.frost_sensitive == 'tolerant':
                    total_score -= 10
            
            # 8. NPK (BONUS)
            npk_bonus = 0
            npk_result = {}
            if n_value is not None and p_value is not None and k_value is not None:
                npk_result = self._score_npk(crop, n_value, p_value, k_value)
                npk_score = npk_result.get("total_score", 0)
                npk_bonus = min(10, max(-10, npk_score / 10))  # Cap between -10 and +10
                total_score += npk_bonus
            
            # 9. LABOR PENALTY
            labor = farmer_data.get("labor_availability", "medium")
            if labor == "low" and crop.labor_req == "high":
                total_score -= 15
            elif labor == "low" and crop.labor_req == "medium":
                total_score -= 5
            
            # 10. MARKET PENALTY
            market = farmer_data.get("market_distance", "near")
            if market == "far" and crop.storage_life in ["very_short", "short"]:
                total_score -= 12
            elif market == "far" and crop.storage_life == "medium":
                total_score -= 5
            
            # 11. GOAL BONUS
            goal = farmer_data.get("farming_goal", "mixed")
            if goal == "profit" and crop.category == "cash_crop":
                total_score += 8
            elif goal == "food_security" and crop.category in ["cereal", "pulse"]:
                total_score += 8
            elif goal == "mixed":
                total_score += 3
            
            # 12. RULE ADJUSTMENTS from inference
            total_score += rule_adjustment
            
            # Cap at 100, minimum 0
            total_score = max(0, min(100, total_score))
            
            # Calculate base confidence
            base_confidence = total_score / 100
            
            # Apply certainty factor to get final confidence
            final_confidence = base_confidence * combined_cf
            final_confidence = max(0.0, min(1.0, final_confidence))
            
            # ========== REJECT ALL CROPS BELOW 50% ==========
            if final_confidence < 0.50:
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
                feasibility = "low"  # 50-60% range
            
            # Generate NPK result for explanation
            if n_value is not None or p_value is not None or k_value is not None:
                npk_result = self._score_npk(crop, n_value, p_value, k_value)
            else:
                npk_result = {}
            
            # Generate explanation
            crop_dict = crop.to_dict()
            explanation = self.explainer.explain_crop(
                crop.name_en,
                crop_dict,
                working_memory,
                final_confidence,
                npk_status=npk_result
            )
            
            # Store individual factor scores
            factor_scores = {
                "total": total_score,
                "season": season_score,
                "region": region_score,
                "soil": soil_score,
                "temperature": temp_score,
                "water": water_score,
                "ph": ph_score,
                "npk_bonus": npk_bonus,
                "rule_adjustment": rule_adjustment,
                "certainty_factor": combined_cf,
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
        
        # Sort by confidence descending
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations


# Singleton instance
_expert_system = None


def get_expert_system():
    """Get or create expert system singleton"""
    global _expert_system
    if _expert_system is None:
        _expert_system = AgriFlowExpertSystem()
    return _expert_system


def get_recommendations(crops_queryset, farmer_data: Dict) -> Dict:
    """Wrapper function for use in views"""
    es = get_expert_system()
    
    if not es.is_initialized:
        es.initialize(crops_queryset)
    
    recommendations = es.recommend(farmer_data)
    
    # Filter to feasible crops (confidence >= 0.50)
    feasible = [r for r in recommendations if r.confidence >= 0.50]
    
    summary = {
        "total_evaluated": len(recommendations),
        "possible_count": len(feasible),
        "high_feasibility": len([r for r in feasible if r.feasibility == "high"]),
        "medium_feasibility": len([r for r in feasible if r.feasibility == "medium"]),
        "low_feasibility": len([r for r in feasible if r.feasibility == "low"]),
    }
    
    if feasible:
        summary["best_crop"] = feasible[0].crop_name
        summary["best_confidence"] = feasible[0].confidence
        summary["best_crop_npk"] = feasible[0].npk_status
    
    return {
        "success": True,
        "summary": summary,
        "recommendations": [r.to_dict() for r in feasible[:10]],
        "explanation_available": True
    }