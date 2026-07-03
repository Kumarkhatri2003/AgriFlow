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
        6. crop_name only (with tie-breaking)
        """
        
        # Auto-detect season from planting date if not provided
        if planting_date and not season:
            season = CropConfigMatcher._get_season_from_date(planting_date)
        
        # Clean inputs
        crop_name = crop_name.strip() if crop_name else None
        variety = variety.strip() if variety else None
        region = region.strip() if region else None
        season = season.strip() if season else None
        
        # Strategy 1: Full match (crop + variety + region + season)
        if variety and region and season:
            configs = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                variety__iexact=variety,
                region=region,
                season=season,
                is_active=True
            )
            if configs.exists():
                return configs.first(), 'full_match (crop + variety + region + season)'
        
        # Strategy 2: crop + variety + region
        if variety and region:
            configs = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                variety__iexact=variety,
                region=region,
                is_active=True
            )
            if configs.exists():
                return configs.first(), 'match (crop + variety + region)'
        
        # Strategy 3: crop + region + season
        if region and season:
            configs = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                region=region,
                season=season,
                is_active=True
            )
            if configs.exists():
                return configs.first(), 'match (crop + region + season)'
        
        # Strategy 4: crop + region
        if region:
            configs = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                region=region,
                is_active=True
            )
            if configs.exists():
                # Prefer config with no variety and no season
                default_config = configs.filter(variety='', season__isnull=True).first()
                if default_config:
                    return default_config, 'match (crop + region - default)'
                return configs.first(), 'match (crop + region)'
        
        # Strategy 5: crop + variety
        if variety:
            configs = CropTypeConfig.objects.filter(
                crop_name__iexact=crop_name,
                variety__iexact=variety,
                is_active=True
            )
            if configs.exists():
                return configs.first(), 'match (crop + variety)'
        
        # Strategy 6: crop only (fallback)
        configs = CropTypeConfig.objects.filter(
            crop_name__iexact=crop_name,
            is_active=True
        )
        if configs.exists():
            # Prefer config with no variety, no region, no season
            default_config = configs.filter(
                variety='', 
                region__isnull=True, 
                season__isnull=True
            ).first()
            if default_config:
                return default_config, 'fallback (crop only - default)'
            return configs.first(), 'fallback (crop only - first found)'
        
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