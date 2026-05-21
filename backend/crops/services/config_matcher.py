# crops/services/config_matcher.py

from datetime import date
from crops.models import CropTypeConfig


class CropConfigMatcher:
    """
    Smart matching for crop configurations with fallback strategies
    """
    
    @staticmethod
    def find_best_match(crop_name, variety=None, region=None, planting_date=None, season=None):
        """
        Find the best matching CropTypeConfig using priority order:
        1. crop_name + variety + region + season
        2. crop_name + variety + region
        3. crop_name + region + season
        4. crop_name + region
        5. crop_name + variety
        6. crop_name only
        """
        
        # Auto-detect season from planting date if not provided
        if planting_date and not season:
            season = CropConfigMatcher._get_season_from_date(planting_date)
        
        # Strategy 1: Full match (crop + variety + region + season)
        if variety and region and season:
            try:
                config = CropTypeConfig.objects.get(
                    crop_name__iexact=crop_name,
                    variety__iexact=variety,
                    region=region,
                    season=season,
                    is_active=True
                )
                return config, 'full_match (crop + variety + region + season)'
            except CropTypeConfig.DoesNotExist:
                pass
            except CropTypeConfig.MultipleObjectsReturned:
                config = CropTypeConfig.objects.filter(
                    crop_name__iexact=crop_name,
                    variety__iexact=variety,
                    region=region,
                    season=season,
                    is_active=True
                ).first()
                if config:
                    return config, 'full_match (first found)'
        
        # Strategy 2: crop + variety + region
        if variety and region:
            try:
                config = CropTypeConfig.objects.get(
                    crop_name__iexact=crop_name,
                    variety__iexact=variety,
                    region=region,
                    is_active=True
                )
                return config, 'match (crop + variety + region)'
            except CropTypeConfig.DoesNotExist:
                pass
        
        # Strategy 3: crop + region + season
        if region and season:
            try:
                config = CropTypeConfig.objects.get(
                    crop_name__iexact=crop_name,
                    region=region,
                    season=season,
                    is_active=True
                )
                return config, 'match (crop + region + season)'
            except CropTypeConfig.DoesNotExist:
                pass
        
        # Strategy 4: crop + region
        if region:
            try:
                config = CropTypeConfig.objects.get(
                    crop_name__iexact=crop_name,
                    region=region,
                    is_active=True
                )
                return config, 'match (crop + region)'
            except CropTypeConfig.DoesNotExist:
                pass
        
        # Strategy 5: crop + variety
        if variety:
            try:
                config = CropTypeConfig.objects.get(
                    crop_name__iexact=crop_name,
                    variety__iexact=variety,
                    is_active=True
                )
                return config, 'match (crop + variety)'
            except CropTypeConfig.DoesNotExist:
                pass
        
        # Strategy 6: crop only (fallback)
        try:
            config = CropTypeConfig.objects.get(
                crop_name__iexact=crop_name,
                is_active=True
            )
            return config, 'fallback (crop only)'
        except CropTypeConfig.DoesNotExist:
            pass
        except CropTypeConfig.MultipleObjectsReturned:
            config = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                is_active=True
            ).first()
            if config:
                return config, 'fallback (crop only - first found)'
        
        return None, 'no match found'
    
    @staticmethod
    def _get_season_from_date(planting_date):
        """Determine season based on planting date (Nepal context)"""
        month = planting_date.month
        
        if month in [2, 3, 4]:
            return 'spring'      # Feb-Apr - Spring
        elif month in [5, 6, 7]:
            return 'summer'      # May-Jul - Summer
        elif month in [8, 9]:
            return 'monsoon'     # Aug-Sep - Monsoon
        elif month in [10, 11]:
            return 'autumn'      # Oct-Nov - Autumn
        else:  # 12, 1
            return 'winter'      # Dec-Jan - Winter