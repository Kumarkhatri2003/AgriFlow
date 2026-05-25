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
            "strengths": self.strengths[:5],  # Limit to 5 strengths
            "weaknesses": self.weaknesses[:5],  # Limit to 5 weaknesses
            "actionable_advice": self.actionable_advice[:5],
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
        
        # Add NPK status if available
        if self.npk_status and isinstance(self.npk_status, dict):
            lines.append("\n📊 NPK ANALYSIS:")
            for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
                if nutrient in self.npk_status:
                    status = self.npk_status[nutrient]
                    if isinstance(status, dict):
                        message = status.get('message', f"{nutrient.capitalize()}: {status.get('status', 'Unknown')}")
                        lines.append(f"   • {message}")
                    elif isinstance(status, str):
                        lines.append(f"   • {nutrient.capitalize()}: {status}")
        
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
        
        # FIX: Ensure npk_status has proper structure
        if npk_status is None or not isinstance(npk_status, dict):
            npk_status = {
                "nitrogen": {"status": "Unknown", "message": "No soil test data available", "suggestion": "Conduct soil test for accurate recommendations", "score": 0},
                "phosphorus": {"status": "Unknown", "message": "No soil test data available", "suggestion": "Conduct soil test for accurate recommendations", "score": 0},
                "potassium": {"status": "Unknown", "message": "No soil test data available", "suggestion": "Conduct soil test for accurate recommendations", "score": 0},
                "total_score": 0
            }
        
        # Ensure all nutrients are present as dicts
        for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
            if nutrient not in npk_status:
                npk_status[nutrient] = {
                    'status': 'Unknown', 
                    'message': f'{nutrient.capitalize()} data not provided',
                    'suggestion': 'Conduct soil test',
                    'score': 0
                }
            elif not isinstance(npk_status[nutrient], dict):
                # Convert legacy format
                npk_status[nutrient] = {
                    'status': 'Unknown',
                    'message': str(npk_status[nutrient]),
                    'suggestion': 'Conduct soil test',
                    'score': 0
                }
        
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
        
        # Add NPK-based strengths/weaknesses (limit to most critical)
        critical_npk = []
        for nutrient, status in npk_status.items():
            if nutrient != "total_score" and isinstance(status, dict):
                status_value = status.get('status', '')
                if status_value == "Perfect":
                    exp.strengths.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is perfect"),
                        "confidence": 0.9
                    })
                elif status_value == "Fits":
                    exp.strengths.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is adequate"),
                        "confidence": 0.7
                    })
                elif "Very Low" in status_value or "Zero" in status_value or "Very High" in status_value:
                    critical_npk.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is {status_value}"),
                        "mitigation": self._get_npk_mitigation(nutrient),
                        "severity": "high"
                    })
                elif "Low" in status_value or "High" in status_value:
                    exp.weaknesses.append({
                        "reason": status.get('message', f"{nutrient.capitalize()} level is {status_value}"),
                        "mitigation": self._get_npk_mitigation(nutrient)
                    })
        
        # Add critical NPK issues first
        for critical in critical_npk:
            exp.weaknesses.insert(0, {
                "reason": critical["reason"],
                "mitigation": critical["mitigation"]
            })
        
        # Remove duplicate strengths and weaknesses
        exp.strengths = self._deduplicate_list(exp.strengths, 'reason')
        exp.weaknesses = self._deduplicate_list(exp.weaknesses, 'reason')
        
        # Filter contradictions
        exp.strengths, exp.weaknesses = self._filter_contradictions(exp.strengths, exp.weaknesses)
        
        # Generate summary based on confidence and critical issues
        has_critical = len(critical_npk) > 0
        if confidence >= 0.80 and not has_critical:
            exp.summary = f"Strongly recommended. {crop_name} is well-suited to your farm conditions."
        elif confidence >= 0.80 and has_critical:
            exp.summary = f"Highly suitable but requires attention to nutrient management."
        elif confidence >= 0.60:
            exp.summary = f"Good choice. {crop_name} should perform well with standard management."
        elif confidence >= 0.50:
            exp.summary = f"Possible but requires attention to address key constraints."
        else:
            exp.summary = f"Not recommended. Too many constraints make {crop_name} unlikely to succeed."
        
        # Generate actionable advice
        exp.actionable_advice = self._generate_advice(exp.weaknesses, npk_status)
        
        return exp
    
    def _deduplicate_list(self, items: List[Dict], key: str) -> List[Dict]:
        """Remove duplicate items based on a key"""
        seen = set()
        unique_items = []
        for item in items:
            item_key = item.get(key, '')
            if item_key and item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)
        return unique_items
    
    def _filter_contradictions(self, strengths: List[Dict], weaknesses: List[Dict]) -> tuple:
        """Remove contradictory strengths and weaknesses"""
        # Extract strength reasons
        strength_reasons = {s.get('reason', '') for s in strengths}
        
        # Filter weaknesses that contradict strengths
        filtered_weaknesses = []
        for w in weaknesses:
            reason = w.get('reason', '')
            # If there's a strength with similar meaning, skip the weakness
            is_contradiction = False
            for s_reason in strength_reasons:
                if 'perfect' in s_reason.lower() and ('low' in reason.lower() or 'high' in reason.lower()):
                    is_contradiction = True
                    break
            if not is_contradiction:
                filtered_weaknesses.append(w)
        
        return strengths, filtered_weaknesses
    
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
        """Generate prioritized, non-contradictory advice"""
        critical_advice = []
        warning_advice = []
        info_advice = []
        
        # Categorize advice from weaknesses
        for w in weaknesses:
            mitigation = w.get('mitigation', '')
            reason = w.get('reason', '')
            
            if mitigation:
                if 'STOP' in mitigation or 'Critical' in reason or 'too high' in reason.lower() or 'too low' in reason.lower():
                    critical_advice.append(mitigation)
                elif 'Apply' in mitigation or 'add' in mitigation.lower():
                    warning_advice.append(mitigation)
                else:
                    info_advice.append(mitigation)
        
        # Add NPK-specific advice - prioritize by severity
        if npk_status and isinstance(npk_status, dict):
            for nutrient, status in npk_status.items():
                if nutrient != "total_score" and isinstance(status, dict):
                    status_value = status.get('status', '')
                    suggestion = status.get('suggestion', '')
                    
                    if "Very High" in status_value:
                        # Add STOP advice first
                        critical_advice.insert(0, suggestion)
                    elif "Very Low" in status_value or "Zero" in status_value:
                        critical_advice.append(suggestion)
                    elif "Low" in status_value or "High" in status_value:
                        warning_advice.append(suggestion)
        
        # Combine advice with priority order (critical first, then warnings, then info)
        advice = []
        advice.extend(critical_advice[:2])   # Max 2 critical
        advice.extend(warning_advice[:2])    # Max 2 warnings
        advice.extend(info_advice[:1])       # Max 1 info
        
        # Remove duplicates while preserving order
        seen = set()
        unique_advice = []
        for a in advice:
            if a and a not in seen:
                seen.add(a)
                unique_advice.append(a)
        
        # Remove contradictory advice (e.g., both "add" and "stop adding")
        final_advice = []
        has_stop = any('STOP' in a for a in unique_advice)
        for a in unique_advice:
            if has_stop and 'Apply' in a and 'STOP' not in a:
                continue  # Skip "Apply" if we have "STOP"
            final_advice.append(a)
        
        return final_advice[:5]