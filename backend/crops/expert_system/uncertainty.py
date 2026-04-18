"""
Uncertainty Management using Certainty Factors
"""

from typing import List


class UncertaintyManager:
    """Manage certainty factors"""
    
    @staticmethod
    def combine_certainty(cf1: float, cf2: float) -> float:
        """Combine two certainty factors"""
        if cf1 is None:
            return cf2 or 0
        if cf2 is None:
            return cf1 or 0
        
        cf1 = max(-1.0, min(1.0, cf1))
        cf2 = max(-1.0, min(1.0, cf2))
        
        if cf1 >= 0 and cf2 >= 0:
            return cf1 + cf2 * (1 - cf1)
        elif cf1 <= 0 and cf2 <= 0:
            return cf1 + cf2 * (1 + cf1)
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
    
    @staticmethod
    def combine_multiple(certainties: List[float]) -> float:
        """Combine multiple certainty factors"""
        if not certainties:
            return 0.0
        result = certainties[0]
        for cf in certainties[1:]:
            result = UncertaintyManager.combine_certainty(result, cf)
        return result


class CertaintyFactors:
    """Predefined certainty factors"""
    ABSOLUTE = 1.0
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30
    SLIGHT_PENALTY = -0.20
    MODERATE_PENALTY = -0.40
    SEVERE_PENALTY = -0.70
    FATAL = -1.0