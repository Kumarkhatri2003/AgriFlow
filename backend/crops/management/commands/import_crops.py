from django.core.management.base import BaseCommand
from crops.models import CropKnowledgeBase

class Command(BaseCommand):
    help = 'Import complete crop data for AgriFlow recommendation system'

    def handle(self, *args, **kwargs):
        dummy_crops = [
            # ===== CEREALS (8) =====
            {
                "name_en": "Rice", "name_np": "धान", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "spring,autumn",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "Clay/Loam", "soil_other": "Clay,Loam,Silty",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 30.0, "k_need": 40.0
            },
            {
                "name_en": "Wheat", "name_np": "गहुँ", "category": "cereal",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 28, "temp_ideal": 18,
                "soil_ideal": "Clay/Loam", "soil_other": "Clay,Loam,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "high", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 50.0, "k_need": 50.0
            },
            {
                "name_en": "Maize", "name_np": "मकै", "category": "cereal",
                "best_season": "spring", "other_seasons": "summer,monsoon",
                "temp_min": 10, "temp_max": 35, "temp_ideal": 25,
                "soil_ideal": "Loam", "soil_other": "Loam,Sandy Loam,Clay Loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 5.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 90.0, "p_need": 45.0, "k_need": 45.0
            },
            {
                "name_en": "Millet", "name_np": "कोदो", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 15, "temp_max": 35, "temp_ideal": 22,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 4.4, "ph_max": 10.0, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "storage_life": "long", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 500, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 50.0, "p_need": 20.0, "k_need": 20.0
            },
            {
                "name_en": "Barley", "name_np": "जौ", "category": "cereal",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 30, "temp_ideal": 18,
                "soil_ideal": "Loamy", "soil_other": "Loam,Sandy Loam,Clay",
                "ph_min": 6.0, "ph_max": 8.0, "ph_ideal": 7.5,
                "water_req": "low", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "storage_life": "long", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 100,
                "altitude_min": 0, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 60.0, "p_need": 30.0, "k_need": 10.0
            },
            {
                "name_en": "Buckwheat", "name_np": "फापर", "category": "cereal",
                "best_season": "autumn", "other_seasons": "summer,spring",
                "temp_min": 10, "temp_max": 30, "temp_ideal": 20,
                "soil_ideal": "Loamy", "soil_other": "Loam,Sandy Loam",
                "ph_min": 4.8, "ph_max": 6.5, "ph_ideal": 5.2,
                "water_req": "low", "region_suitable": "all",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 90,
                "altitude_min": 500, "altitude_max": 3000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 60.0, "p_need": 30.0, "k_need": 30.0
            },
            {
                "name_en": "Sorghum", "name_np": "ज्वार", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 15, "temp_max": 40, "temp_ideal": 27,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 7.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 75.0, "p_need": 30.0, "k_need": 30.0
            },
            {
                "name_en": "Oats", "name_np": "जई", "category": "cereal",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 30, "temp_ideal": 18,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam,Sandy Loam",
                "ph_min": 4.5, "ph_max": 8.6, "ph_ideal": 5.29,
                "water_req": "low", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 100,
                "altitude_min": 0, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 80.0, "p_need": 60.0, "k_need": 40.0
            },

            # ===== PULSES (8) =====
            {
                "name_en": "Lentil", "name_np": "मसुर", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 10, "temp_max": 30, "temp_ideal": 20,
                "soil_ideal": "Loamy", "soil_other": "Loam,Alluvial,Clay Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 90,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0
            },
            {
                "name_en": "Chickpea", "name_np": "चना", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 10, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay,Sandy Loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 100,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 20.0, "p_need": 60.0, "k_need": 20.0
            },
            {
                "name_en": "Pigeon Pea", "name_np": "अरहर", "category": "pulse",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 18, "temp_max": 42, "temp_ideal": 28,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay,Sandy Loam",
                "ph_min": 5.0, "ph_max": 8.5, "ph_ideal": 6.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 180,
                "altitude_min": 0, "altitude_max": 1200,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 20.0, "p_need": 60.0, "k_need": 25.0
            },
            {
                "name_en": "Black Gram", "name_np": "मास", "category": "pulse",
                "best_season": "summer", "other_seasons": "monsoon,spring",
                "temp_min": 20, "temp_max": 38, "temp_ideal": 28,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 90,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0
            },
            {
                "name_en": "Green Gram", "name_np": "मुग", "category": "pulse",
                "best_season": "summer", "other_seasons": "monsoon,spring",
                "temp_min": 20, "temp_max": 38, "temp_ideal": 28,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 4.3, "ph_max": 8.1, "ph_ideal": 6.82,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 75,
                "altitude_min": 0, "altitude_max": 1200,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 20.0, "p_need": 20.0, "k_need": 20.0
            },
            {
                "name_en": "Soybean", "name_np": "भटमास", "category": "pulse",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 15, "temp_max": 38, "temp_ideal": 25,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "all",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 1800,
                "day_length_sensitive": False, "day_length_type": "short-day",
                "n_need": 10.0, "p_need": 40.0, "k_need": 30.0
            },
            {
                "name_en": "Field Pea", "name_np": "केराउ", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 28, "temp_ideal": 18,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "all",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 90,
                "altitude_min": 0, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 60.0, "p_need": 80.0, "k_need": 70.0
            },

            # ===== TUBERS (5) =====
            {
                "name_en": "Potato", "name_np": "आलु", "category": "tuber",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 8, "temp_max": 28, "temp_ideal": 18,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam,Clay Loam",
                "ph_min": 5.0, "ph_max": 6.0, "ph_ideal": 5.5,
                "water_req": "medium", "region_suitable": "all",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 500, "altitude_max": 3000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 100.0, "k_need": 60.0
            },
            {
                "name_en": "Sweet Potato", "name_np": "सखरखण्ड", "category": "tuber",
                "best_season": "autumn", "other_seasons": "spring,monsoon",
                "temp_min": 10, "temp_max": 35, "temp_ideal": 24,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 6.5, "ph_ideal": 5.5,
                "water_req": "low", "region_suitable": "all",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 40.0, "p_need": 80.0, "k_need": 120.0
            },
            {
                "name_en": "Taro", "name_np": "कर्कलो", "category": "tuber",
                "best_season": "monsoon", "other_seasons": "spring,autumn",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "low", "region_suitable": "mid-hill,terai",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 240,
                "altitude_min": 500, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 50.0, "k_need": 100.0
            },
            {
                "name_en": "Yam", "name_np": "तरुल", "category": "tuber",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 15, "temp_max": 38, "temp_ideal": 28,
                "soil_ideal": "Loam", "soil_other": "Loam,Sandy Loam,Clay Loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 270,
                "altitude_min": 0, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 135.0, "p_need": 135.0, "k_need": 90.0
            },
            {
                "name_en": "Cassava", "name_np": "कसावा", "category": "tuber",
                "best_season": "monsoon", "other_seasons": "summer,spring",
                "temp_min": 18, "temp_max": 40, "temp_ideal": 28,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 4.2, "ph_max": 8.0, "ph_ideal": 5.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 300,
                "altitude_min": 0, "altitude_max": 1200,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 50.0, "p_need": 50.0, "k_need": 100.0
            },

            # ===== VEGETABLES (8) =====
            {
                "name_en": "Tomato", "name_np": "गोलभेडा", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 15, "temp_max": 32, "temp_ideal": 22,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam,Clay Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "very_short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 90,
                "altitude_min": 0, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 200.0, "p_need": 150.0, "k_need": 120.0
            },
            {
                "name_en": "Onion", "name_np": "प्याज", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 28, "temp_ideal": 20,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 6.5, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 150,
                "altitude_min": 500, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "long-day",
                "n_need": 60.0, "p_need": 60.0, "k_need": 40.0
            },
            {
                "name_en": "Cabbage", "name_np": "बन्दा", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 5, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.4,
                "water_req": "high", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "tolerant",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 110,
                "altitude_min": 800, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 60.0, "p_need": 80.0, "k_need": 50.0
            },
            {
                "name_en": "Cauliflower", "name_np": "काउली", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 7, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.6, "ph_max": 6.8, "ph_ideal": 6.84,
                "water_req": "high", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "tolerant",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 80,
                "altitude_min": 800, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 200.0, "p_need": 120.0, "k_need": 80.0
            },
            {
                "name_en": "Brinjal", "name_np": "भण्टा", "category": "vegetable",
                "best_season": "spring", "other_seasons": "summer,monsoon",
                "temp_min": 18, "temp_max": 35, "temp_ideal": 27,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 6.6, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "very_short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 120,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 150.0, "k_need": 100.0
            },
            {
                "name_en": "Chili", "name_np": "खुर्सानी", "category": "vegetable",
                "best_season": "summer", "other_seasons": "spring,monsoon",
                "temp_min": 18, "temp_max": 35, "temp_ideal": 25,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 7.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "short", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 100,
                "altitude_min": 500, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 120.0, "p_need": 90.0, "k_need": 90.0
            },

            # ===== CASH CROPS (3) =====
            {
                "name_en": "Sugarcane", "name_np": "ऊखु", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "summer,monsoon",
                "temp_min": 15, "temp_max": 40, "temp_ideal": 30,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam,Clay Loam",
                "ph_min": 5.0, "ph_max": 7.0, "ph_ideal": 5.96,
                "water_req": "high", "region_suitable": "terai",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "high",
                "water_logging_tolerance": "low", "growing_days": 365,
                "altitude_min": 0, "altitude_max": 1200,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 120.0, "p_need": 60.0, "k_need": 40.0
            },
            {
                "name_en": "Tea", "name_np": "चिया", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon,autumn",
                "temp_min": 13, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam,Sandy Loam",
                "ph_min": 4.5, "ph_max": 5.5, "ph_ideal": 5.5,
                "water_req": "high", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "storage_life": "long", "labor_req": "high",
                "water_logging_tolerance": "high", "growing_days": 365,
                "altitude_min": 800, "altitude_max": 2200,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 35.0, "p_need": 70.0, "k_need": 15.0
            },
            {
                "name_en": "Coffee", "name_np": "कफी", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon,autumn",
                "temp_min": 15, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam",
                "ph_min": 5.2, "ph_max": 6.3, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "long", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 365,
                "altitude_min": 800, "altitude_max": 1800,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 100.0, "p_need": 30.0, "k_need": 60.0
            },

            # ===== OILSEEDS (3) =====
            {
                "name_en": "Mustard", "name_np": "तोरी", "category": "oilseed",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 10, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "Loamy", "soil_other": "Loam,Clay Loam,Sandy Loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "medium", "growing_days": 120,
                "altitude_min": 500, "altitude_max": 2500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 200.0, "p_need": 150.0, "k_need": 100.0
            },
            {
                "name_en": "Sunflower", "name_np": "सूर्यमुखी", "category": "oilseed",
                "best_season": "spring", "other_seasons": "summer,monsoon",
                "temp_min": 18, "temp_max": 35, "temp_ideal": 25,
                "soil_ideal": "Loamy", "soil_other": "Loam,Sandy Loam,Clay Loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "storage_life": "medium", "labor_req": "medium",
                "water_logging_tolerance": "low", "growing_days": 100,
                "altitude_min": 0, "altitude_max": 2000,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 80.0, "p_need": 60.0, "k_need": 80.0
            },
            {
                "name_en": "Sesame", "name_np": "तिल", "category": "oilseed",
                "best_season": "summer", "other_seasons": "monsoon,spring",
                "temp_min": 20, "temp_max": 38, "temp_ideal": 27,
                "soil_ideal": "Sandy Loam", "soil_other": "Sandy Loam,Loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.2,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "storage_life": "long", "labor_req": "low",
                "water_logging_tolerance": "low", "growing_days": 90,
                "altitude_min": 0, "altitude_max": 1500,
                "day_length_sensitive": False, "day_length_type": "",
                "n_need": 40.0, "p_need": 40.0, "k_need": 40.0
            }
        ]

        created_count = 0
        updated_count = 0
        error_count = 0

        for data in dummy_crops:
            try:
                obj, created = CropKnowledgeBase.objects.update_or_create(
                    name_en=data["name_en"],
                    defaults=data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Created: {obj.name_en}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"⟳ Updated: {obj.name_en}"))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"✗ Error with {data.get('name_en', 'Unknown')}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Crop data import complete.\n"
            f"   Created: {created_count}\n"
            f"   Updated: {updated_count}\n"
            f"   Errors: {error_count}\n"
            f"   Total crops in DB: {CropKnowledgeBase.objects.count()}"
        ))