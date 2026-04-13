"""
Explanation Facility - Why did the expert system recommend this?
Includes NPK explanation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Explanation:
    """Complete explanation for a recommendation"""
    crop_name: str
    summary: str
    confidence: float
    strengths: List[Dict] = field(default_factory=list)
    weaknesses: List[Dict] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    actionable_advice: List[str] = field(default_factory=list)
    npk_status: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "crop_name": self.crop_name,
            "summary": self.summary,
            "confidence": round(self.confidence * 100, 1),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "actionable_advice": self.actionable_advice,
            "npk_status": self.npk_status
        }
    
    def to_text(self) -> str:
        lines = [
            f"\n{'='*50}",
            f"🌾 Recommendation: {self.crop_name}",
            f"📊 Confidence: {self.confidence * 100:.0f}%",
            f"{'='*50}",
            f"\n📝 {self.summary}",
        ]
        
        # Add NPK status if available and has data
        if self.npk_status and self.npk_status.get('nitrogen'):
            lines.append("\n📊 NPK ANALYSIS:")
            for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
                if nutrient in self.npk_status:
                    status = self.npk_status[nutrient]
                    if status.get('message'):
                        lines.append(f"   • {status['message']}")
        
        if self.strengths:
            lines.append("\n✅ STRENGTHS:")
            for s in self.strengths[:3]:
                lines.append(f"   • {s.get('reason', '')}")
        
        if self.weaknesses:
            lines.append("\n⚠️ WEAKNESSES:")
            for w in self.weaknesses[:3]:
                lines.append(f"   • {w.get('reason', '')}")
                if w.get('mitigation'):
                    lines.append(f"     → Solution: {w['mitigation']}")
        
        if self.actionable_advice:
            lines.append("\n💡 ACTIONABLE ADVICE:")
            for a in self.actionable_advice[:3]:
                lines.append(f"   • {a}")
        
        return "\n".join(lines)


class ExplanationFacility:
    """Generate human-readable explanations"""
    
    def __init__(self):
        pass
    
    def explain_crop(
        self,
        crop_name: str,
        crop_data: Dict,
        working_memory,
        confidence: float,
        npk_status: Dict = None
    ) -> Explanation:
        """Generate explanation for a crop recommendation"""
        
        # Ensure npk_status is a dict with proper structure
        if npk_status is None:
            npk_status = {}
        
        # Ensure npk_status has the expected keys
        if not isinstance(npk_status, dict):
            npk_status = {}
        
        # Ensure each nutrient has required fields
        for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
            if nutrient not in npk_status:
                npk_status[nutrient] = {'status': 'unknown', 'message': '', 'score': 0}
            elif not isinstance(npk_status[nutrient], dict):
                npk_status[nutrient] = {'status': 'unknown', 'message': str(npk_status[nutrient]), 'score': 0}
            elif 'status' not in npk_status[nutrient]:
                npk_status[nutrient]['status'] = 'unknown'
            elif 'message' not in npk_status[nutrient]:
                npk_status[nutrient]['message'] = ''
            elif 'score' not in npk_status[nutrient]:
                npk_status[nutrient]['score'] = 0
        
        exp = Explanation(
            crop_name=crop_name,
            summary="",
            confidence=confidence,
            strengths=[],
            weaknesses=[],
            mitigations=[],
            actionable_advice=[],
            npk_status=npk_status
        )
        
        # Extract strengths and weaknesses from rule trace
        if working_memory:
            for trace in working_memory.rule_trace:
                rule_id = trace.get("rule", "")
                certainty = trace.get("certainty", 0)
                
                if "PERFECT" in rule_id or "MATCH" in rule_id or "OPTIMAL" in rule_id:
                    exp.strengths.append({
                        "reason": self._get_rule_explanation(rule_id),
                        "confidence": certainty
                    })
                elif "RISK" in rule_id or "POOR" in rule_id or "DEFICIENT" in rule_id or "STRESS" in rule_id:
                    mitigation = self._get_rule_mitigation(rule_id)
                    exp.weaknesses.append({
                        "reason": self._get_rule_explanation(rule_id),
                        "mitigation": mitigation
                    })
                    if mitigation:
                        exp.mitigations.append(mitigation)
        
        # Add NPK-based strengths/weaknesses
        for nutrient, status in npk_status.items():
            if nutrient != "total_score" and isinstance(status, dict):
                status_value = status.get('status', '')
                if status_value == "optimal":
                    exp.strengths.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is optimal"),
                        "confidence": 0.8
                    })
                elif "deficit" in status_value:
                    exp.weaknesses.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is low"),
                        "mitigation": self._get_npk_mitigation(nutrient)
                    })
        
        # Generate summary based on confidence
        if confidence >= 0.80:
            exp.summary = f"Strongly recommended. {crop_name} is well-suited to your farm conditions."
        elif confidence >= 0.60:
            exp.summary = f"Good choice. {crop_name} should perform well with standard management."
        elif confidence >= 0.40:
            exp.summary = f"Possible but requires attention to address key constraints."
        else:
            exp.summary = f"Not recommended. Too many constraints make {crop_name} unlikely to succeed."
        
        # Generate actionable advice
        exp.actionable_advice = self._generate_advice(exp.weaknesses, npk_status)
        
        return exp
    
    def _get_rule_explanation(self, rule_id: str) -> str:
        explanations = {
            "SEASON_PERFECT": "Current season is ideal for planting this crop",
            "SEASON_ACCEPTABLE": "Current season is acceptable for this crop",
            "SOIL_PERFECT": "Your soil type is ideal for this crop",
            "SOIL_ACCEPTABLE": "Your soil type is acceptable for this crop",
            "PH_OPTIMAL": "Soil pH is in optimal range",
            "WATER_DROUGHT_RISK": "High drought risk for rainfed conditions",
            "WATER_DROUGHT_TOLERANT": "Crop is drought tolerant for rainfed farming",
            "SOIL_POOR": "Soil type is not suitable for this crop",
            "PH_TOO_ACIDIC": "Soil is too acidic for this crop",
            "PH_TOO_ALKALINE": "Soil is too alkaline for this crop",
            "TEMP_OPTIMAL": "Temperature is within optimal range",
            "TEMP_STRESS": "Temperature is below optimal range",
            "FROST_RISK": "Frost risk - crop is frost sensitive",
            "REGION_MATCH": "Your region is suitable for this crop",
            "REGION_MISMATCH": "Your region is not suitable for this crop",
            "NPK_BALANCED": "Soil NPK levels are adequate",
            "N_DEFICIENT": "Nitrogen levels are low",
            "P_DEFICIENT": "Phosphorus levels are low",
            "K_DEFICIENT": "Potassium levels are low",
        }
        return explanations.get(rule_id, f"Rule {rule_id} applied")
    
    def _get_rule_mitigation(self, rule_id: str) -> str:
        mitigations = {
            "WATER_DROUGHT_RISK": "Use mulch, plant after first heavy rain",
            "SOIL_POOR": "Add organic matter, consider raised beds",
            "PH_TOO_ACIDIC": "Apply lime 2-3 months before planting",
            "PH_TOO_ALKALINE": "Add sulfur or organic matter",
            "TEMP_STRESS": "Use mulch or row covers to retain heat",
            "FROST_RISK": "Delay planting or use frost protection",
            "REGION_MISMATCH": "Consider protected cultivation or different varieties",
            "N_DEFICIENT": "Apply urea (50 kg/ropani) or compost",
            "P_DEFICIENT": "Apply DAP (25 kg/ropani) or bone meal",
            "K_DEFICIENT": "Apply MOP (20 kg/ropani) or wood ash",
        }
        return mitigations.get(rule_id, "")
    
    def _get_npk_mitigation(self, nutrient: str) -> str:
        mitigations = {
            "nitrogen": "Apply urea (50 kg/ropani) or compost before planting",
            "phosphorus": "Apply DAP (25 kg/ropani) or bone meal",
            "potassium": "Apply MOP (20 kg/ropani) or wood ash",
        }
        return mitigations.get(nutrient, "Consider soil testing and balanced fertilization")
    
    def _generate_advice(self, weaknesses: List[Dict], npk_status: Dict = None) -> List[str]:
        advice = []
        for w in weaknesses:
            if w.get('mitigation'):
                advice.append(w['mitigation'])
        
        # Add NPK-specific advice
        if npk_status:
            for nutrient, status in npk_status.items():
                if nutrient != "total_score" and isinstance(status, dict):
                    status_value = status.get('status', '')
                    if "deficit" in status_value:
                        advice.append(self._get_npk_mitigation(nutrient))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_advice = []
        for a in advice:
            if a not in seen:
                seen.add(a)
                unique_advice.append(a)
        
        return unique_advice[:5]