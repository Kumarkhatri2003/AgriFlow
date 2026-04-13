from django.core.management.base import BaseCommand
from crops.models import CropKnowledgeBase

class Command(BaseCommand):
    help = 'Import 30 dummy crops for AgriFlow recommendation system'

    def handle(self, *args, **kwargs):
        dummy_crops = [
            # ===== CEREALS (7) =====
            {
                "name_en": "Rice (Bansdhan)", "name_np": "धान", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "spring",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "clay,silty",
                "ph_min": 5.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 100.0, "p_need": 30.0, "k_need": 40.0   # High N, Medium P, Medium K
            },
            {
                "name_en": "Wheat (Gautam)", "name_np": "गहुँ", "category": "cereal",
                "best_season": "winter", "other_seasons": "spring",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "clay",
                "ph_min": 6.0, "ph_max": 8.0, "ph_ideal": 6.8,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "no",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 120.0, "p_need": 40.0, "k_need": 40.0   # High N, Medium P, Medium K
            },
            {
                "name_en": "Maize (Arun-2)", "name_np": "मकै", "category": "cereal",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "no",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 100.0, "p_need": 40.0, "k_need": 40.0   # High N, Medium P, Medium K
            },
            {
                "name_en": "Millet (Kodo)", "name_np": "कोदो", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "spring",
                "temp_min": 15, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.0, "ph_max": 7.0, "ph_ideal": 5.8,
                "water_req": "low", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 30.0, "p_need": 40.0, "k_need": 40.0    # Low N, Medium P, Medium K
            },
            {
                "name_en": "Barley", "name_np": "जौ", "category": "cereal",
                "best_season": "winter", "other_seasons": "spring",
                "temp_min": 8, "temp_max": 22, "temp_ideal": 15,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 60.0, "p_need": 20.0, "k_need": 20.0    # Medium N, Low P, Low K
            },
            {
                "name_en": "Buckwheat (Phapar)", "name_np": "फापर", "category": "cereal",
                "best_season": "autumn", "other_seasons": "spring",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 15,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.0, "ph_max": 7.0, "ph_ideal": 5.5,
                "water_req": "low", "region_suitable": "hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "medium",
                "n_need": 20.0, "p_need": 20.0, "k_need": 20.0    # Low N, Low P, Low K
            },
            {
                "name_en": "Finger Millet (Rato Kodo)", "name_np": "रातो कोदो", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "spring",
                "temp_min": 12, "temp_max": 28, "temp_ideal": 20,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 5.0, "ph_max": 7.0, "ph_ideal": 5.8,
                "water_req": "medium", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 30.0, "p_need": 40.0, "k_need": 40.0    # Low N, Medium P, Medium K
            },

            # ===== PULSES (5) =====
            {
                "name_en": "Lentil (Simal)", "name_np": "मसुरो", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 15, "temp_max": 25, "temp_ideal": 20,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.2,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0    # Low N, Medium P, Low K
            },
            {
                "name_en": "Black Gram (Mas)", "name_np": "मास", "category": "pulse",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "clay", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0    # Low N, Medium P, Low K
            },
            {
                "name_en": "Soybean", "name_np": "भटमास", "category": "pulse",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 60.0, "p_need": 60.0, "k_need": 40.0    # Medium N, High P, Medium K
            },
            {
                "name_en": "Chickpea (Chana)", "name_np": "चना", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 12, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0    # Low N, Medium P, Low K
            },
            {
                "name_en": "Pigeon Pea (Rahar)", "name_np": "रहर", "category": "pulse",
                "best_season": "monsoon", "other_seasons": "spring",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 24,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.2,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 20.0, "p_need": 20.0, "k_need": 40.0    # Low N, Low P, Medium K
            },

            # ===== VEGETABLES (7) =====
            {
                "name_en": "Tomato", "name_np": "टमाटर", "category": "vegetable",
                "best_season": "spring", "other_seasons": "autumn",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 24,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "short",
                "n_need": 120.0, "p_need": 80.0, "k_need": 80.0    # High N, High P, High K
            },
            {
                "name_en": "Potato (Khumal)", "name_np": "आलु", "category": "vegetable",
                "best_season": "winter", "other_seasons": "spring",
                "temp_min": 15, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.0, "ph_max": 6.5, "ph_ideal": 5.8,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "medium",
                "n_need": 100.0, "p_need": 60.0, "k_need": 90.0    # High N, High P, High K
            },
            {
                "name_en": "Cauliflower", "name_np": "काउली", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 15, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "clay",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "short",
                "n_need": 120.0, "p_need": 80.0, "k_need": 60.0    # High N, High P, Medium K
            },
            {
                "name_en": "Cabbage", "name_np": "बन्दागोभी", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 12, "temp_max": 22, "temp_ideal": 16,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 120.0, "p_need": 60.0, "k_need": 60.0    # High N, Medium P, Medium K
            },
            {
                "name_en": "Onion", "name_np": "प्याज", "category": "vegetable",
                "best_season": "winter", "other_seasons": "spring",
                "temp_min": 12, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 80.0, "p_need": 60.0, "k_need": 60.0     # Medium N, High P, Medium K
            },
            {
                "name_en": "Chili (Khursani)", "name_np": "खुर्सानी", "category": "vegetable",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 80.0, "p_need": 60.0, "k_need": 80.0     # Medium N, High P, High K
            },
            {
                "name_en": "Bitter Gourd (Karela)", "name_np": "करेला", "category": "vegetable",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 22, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 80.0, "p_need": 50.0, "k_need": 50.0     # Medium N, Medium P, Medium K
            },

            # ===== OILSEEDS (3) =====
            {
                "name_en": "Mustard (Tori)", "name_np": "तोरी", "category": "oilseed",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 80.0, "p_need": 30.0, "k_need": 30.0     # Medium N, Medium P, Medium K
            },
            {
                "name_en": "Sunflower", "name_np": "सूर्यमुखी", "category": "oilseed",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 24,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 80.0, "p_need": 60.0, "k_need": 40.0     # Medium N, High P, Medium K
            },
            {
                "name_en": "Sesame (Til)", "name_np": "तिल", "category": "oilseed",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 27,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.2,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "long",
                "n_need": 40.0, "p_need": 40.0, "k_need": 20.0     # Medium N, Medium P, Low K
            },

            # ===== FRUITS (4) =====
            {
                "name_en": "Banana (Malbhog)", "name_np": "केरा", "category": "fruit",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 100.0, "p_need": 40.0, "k_need": 120.0   # High N, Medium P, High K
            },
            {
                "name_en": "Mango", "name_np": "आँप", "category": "fruit",
                "best_season": "spring", "other_seasons": "",
                "temp_min": 22, "temp_max": 38, "temp_ideal": 30,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "short",
                "n_need": 60.0, "p_need": 40.0, "k_need": 60.0     # Medium N, Medium P, Medium K
            },
            {
                "name_en": "Orange", "name_np": "सुन्तला", "category": "fruit",
                "best_season": "spring", "other_seasons": "",
                "temp_min": 15, "temp_max": 28, "temp_ideal": 22,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 80.0, "p_need": 40.0, "k_need": 60.0     # Medium N, Medium P, Medium K
            },
            {
                "name_en": "Lemon", "name_np": "कागती", "category": "fruit",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "medium",
                "n_need": 60.0, "p_need": 30.0, "k_need": 40.0     # Medium N, Low P, Low K
            },

            # ===== CASH CROPS (4) =====
            {
                "name_en": "Tea (Camellia)", "name_np": "चिया", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 4.5, "ph_max": 5.5, "ph_ideal": 5.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 120.0, "p_need": 40.0, "k_need": 60.0    # High N, Medium P, Medium K
            },
            {
                "name_en": "Cardamom (Alainchi)", "name_np": "अलैंची", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "forest_soil",
                "ph_min": 5.0, "ph_max": 6.5, "ph_ideal": 5.5,
                "water_req": "medium", "region_suitable": "hill,mountain",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 60.0, "p_need": 40.0, "k_need": 80.0     # Medium N, Medium P, High K
            },
            {
                "name_en": "Sugarcane", "name_np": "उखु", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "",
                "temp_min": 20, "temp_max": 38, "temp_ideal": 30,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 6.0, "ph_max": 8.0, "ph_ideal": 7.0,
                "water_req": "high", "region_suitable": "terai",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "medium",
                "n_need": 120.0, "p_need": 60.0, "k_need": 100.0   # High N, High P, High K
            },
            {
                "name_en": "Cotton", "name_np": "कपास", "category": "cash_crop",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 38, "temp_ideal": 30,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 8.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 80.0, "p_need": 40.0, "k_need": 40.0     # Medium N, Medium P, Medium K
            },
            # ===== ADDITIONAL 30 CROPS =====

# ===== MORE CEREALS (3) =====
            {
                "name_en": "Foxtail Millet (Kaguno)", "name_np": "कागुनो", "category": "cereal",
                "best_season": "monsoon", "other_seasons": "spring",
                "temp_min": 15, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.0,
                "water_req": "low", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 30.0, "p_need": 30.0, "k_need": 30.0
            },
            {
                "name_en": "Proso Millet (Cheeno)", "name_np": "चीना", "category": "cereal",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 15, "temp_max": 35, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.2,
                "water_req": "low", "region_suitable": "mid-hill,hill,mountain",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 40.0, "p_need": 30.0, "k_need": 30.0
            },
            {
                "name_en": "Sorghum (Jowar)", "name_np": "ज्वार", "category": "cereal",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "clay",
                "ph_min": 6.0, "ph_max": 8.0, "ph_ideal": 7.0,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 80.0, "p_need": 40.0, "k_need": 40.0
            },

            # ===== MORE PULSES (5) =====
            {
                "name_en": "Green Gram (Mung)", "name_np": "मुँग", "category": "pulse",
                "best_season": "summer", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 40.0, "k_need": 20.0
            },
            {
                "name_en": "Cowpea (Bodi)", "name_np": "बोडी", "category": "pulse",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "high", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 40.0, "k_need": 40.0
            },
            {
                "name_en": "Grass Pea (Khesari)", "name_np": "खेसरी", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "clay_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "terai",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "long",
                "n_need": 15.0, "p_need": 30.0, "k_need": 20.0
            },
            {
                "name_en": "Moth Bean", "name_np": "मोठ", "category": "pulse",
                "best_season": "summer", "other_seasons": "spring",
                "temp_min": 25, "temp_max": 40, "temp_ideal": 32,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 7.0, "ph_max": 8.5, "ph_ideal": 7.5,
                "water_req": "low", "region_suitable": "terai",
                "drought_tolerance": "very_high", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "long",
                "n_need": 20.0, "p_need": 30.0, "k_need": 20.0
            },
            {
                "name_en": "Fava Bean (Bakulla)", "name_np": "बकुल्ला", "category": "pulse",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 5, "temp_max": 20, "temp_ideal": 15,
                "soil_ideal": "clay_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.8,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 30.0, "p_need": 40.0, "k_need": 40.0
            },

            # ===== MORE VEGETABLES (8) =====
            {
                "name_en": "Eggplant (Brinjal)", "name_np": "भन्टा", "category": "vegetable",
                "best_season": "spring", "other_seasons": "summer",
                "temp_min": 20, "temp_max": 32, "temp_ideal": 26,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 80.0, "p_need": 60.0, "k_need": 60.0
            },
            {
                "name_en": "Cucumber (Kakro)", "name_np": "काँक्रो", "category": "vegetable",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "high", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 60.0, "p_need": 50.0, "k_need": 50.0
            },
            {
                "name_en": "Pumpkin (Pharsi)", "name_np": "फर्सी", "category": "vegetable",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 60.0, "p_need": 40.0, "k_need": 60.0
            },
            {
                "name_en": "Radish (Mula)", "name_np": "मुला", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 22, "temp_ideal": 16,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill,mountain",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "short",
                "n_need": 60.0, "p_need": 40.0, "k_need": 50.0
            },
            {
                "name_en": "Carrot (Gajar)", "name_np": "गाजर", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 60.0, "p_need": 40.0, "k_need": 80.0
            },
            {
                "name_en": "Spinach (Palung)", "name_np": "पालुङ्गो", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn,spring",
                "temp_min": 8, "temp_max": 22, "temp_ideal": 15,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.8,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill,mountain",
                "drought_tolerance": "low", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "short",
                "n_need": 80.0, "p_need": 40.0, "k_need": 50.0
            },
            {
                "name_en": "Okra (Bhindi)", "name_np": "भिन्डी", "category": "vegetable",
                "best_season": "summer", "other_seasons": "spring",
                "temp_min": 22, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 60.0, "p_need": 40.0, "k_need": 40.0
            },
            {
                "name_en": "Garlic (Lasun)", "name_np": "लसुन", "category": "vegetable",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 22, "temp_ideal": 15,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "high", "storage_life": "long",
                "n_need": 60.0, "p_need": 80.0, "k_need": 60.0
            },

            # ===== MORE OILSEEDS (3) =====
            {
                "name_en": "Linseed (Alsi)", "name_np": "अलसी", "category": "oilseed",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 8, "temp_max": 22, "temp_ideal": 15,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "labor_req": "low", "storage_life": "long",
                "n_need": 40.0, "p_need": 30.0, "k_need": 40.0
            },
            {
                "name_en": "Safflower (Kusum)", "name_np": "कुसुम", "category": "oilseed",
                "best_season": "winter", "other_seasons": "spring",
                "temp_min": 12, "temp_max": 28, "temp_ideal": 20,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.8,
                "water_req": "low", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "high", "frost_sensitive": "tolerant",
                "labor_req": "medium", "storage_life": "long",
                "n_need": 60.0, "p_need": 40.0, "k_need": 40.0
            },
            {
                "name_en": "Nigella (Kalojira)", "name_np": "कालो जीरा", "category": "oilseed",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 10, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "low", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "high", "frost_sensitive": "no",
                "labor_req": "low", "storage_life": "long",
                "n_need": 40.0, "p_need": 30.0, "k_need": 30.0
            },

            # ===== MORE FRUITS (6) =====
            {
                "name_en": "Papaya", "name_np": "मेवा", "category": "fruit",
                "best_season": "spring", "other_seasons": "summer",
                "temp_min": 20, "temp_max": 32, "temp_ideal": 26,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 6.0, "ph_max": 7.0, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 80.0, "p_need": 60.0, "k_need": 80.0
            },
            {
                "name_en": "Guava", "name_np": "अम्बा", "category": "fruit",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "short",
                "n_need": 60.0, "p_need": 40.0, "k_need": 60.0
            },
            {
                "name_en": "Pineapple", "name_np": "भुइँकटर", "category": "fruit",
                "best_season": "spring", "other_seasons": "summer",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 4.5, "ph_max": 6.5, "ph_ideal": 5.5,
                "water_req": "medium", "region_suitable": "mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 80.0, "p_need": 60.0, "k_need": 100.0
            },
            {
                "name_en": "Litchi", "name_np": "लीची", "category": "fruit",
                "best_season": "spring", "other_seasons": "",
                "temp_min": 15, "temp_max": 32, "temp_ideal": 25,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "medium", "storage_life": "short",
                "n_need": 80.0, "p_need": 40.0, "k_need": 60.0
            },
            {
                "name_en": "Jackfruit (Rukh Katahar)", "name_np": "रुख कटहर", "category": "fruit",
                "best_season": "spring", "other_seasons": "summer",
                "temp_min": 20, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "low", "storage_life": "short",
                "n_need": 60.0, "p_need": 40.0, "k_need": 80.0
            },
            {
                "name_en": "Pear (Nashpati)", "name_np": "नासपाती", "category": "fruit",
                "best_season": "spring", "other_seasons": "",
                "temp_min": 8, "temp_max": 25, "temp_ideal": 18,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.5,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "tolerant",
                "labor_req": "medium", "storage_life": "medium",
                "n_need": 60.0, "p_need": 40.0, "k_need": 60.0
            },

            # ===== MORE CASH CROPS (5) =====
            {
                "name_en": "Coffee (Arabica)", "name_np": "कफी", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 15, "temp_max": 28, "temp_ideal": 22,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 6.5, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 100.0, "p_need": 40.0, "k_need": 80.0
            },
            {
                "name_en": "Turmeric (Besar)", "name_np": "बेसार", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 20, "temp_max": 32, "temp_ideal": 26,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 80.0, "p_need": 60.0, "k_need": 100.0
            },
            {
                "name_en": "Ginger (Aduwa)", "name_np": "अदुवा", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "monsoon",
                "temp_min": 18, "temp_max": 30, "temp_ideal": 24,
                "soil_ideal": "loamy", "soil_other": "sandy_loam",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.0,
                "water_req": "medium", "region_suitable": "mid-hill,hill",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "medium",
                "n_need": 100.0, "p_need": 60.0, "k_need": 100.0
            },
            {
                "name_en": "Tobacco", "name_np": "सुर्ती", "category": "cash_crop",
                "best_season": "winter", "other_seasons": "autumn",
                "temp_min": 15, "temp_max": 30, "temp_ideal": 22,
                "soil_ideal": "sandy_loam", "soil_other": "loamy",
                "ph_min": 5.5, "ph_max": 7.0, "ph_ideal": 6.2,
                "water_req": "medium", "region_suitable": "terai,mid-hill",
                "drought_tolerance": "medium", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 100.0, "p_need": 60.0, "k_need": 80.0
            },
            {
                "name_en": "Jute (Patsan)", "name_np": "पटसन", "category": "cash_crop",
                "best_season": "spring", "other_seasons": "summer",
                "temp_min": 22, "temp_max": 35, "temp_ideal": 28,
                "soil_ideal": "loamy", "soil_other": "clay_loam",
                "ph_min": 6.0, "ph_max": 7.5, "ph_ideal": 6.8,
                "water_req": "high", "region_suitable": "terai",
                "drought_tolerance": "low", "frost_sensitive": "yes",
                "labor_req": "high", "storage_life": "long",
                "n_need": 80.0, "p_need": 40.0, "k_need": 60.0
            }
        ]

        created_count = 0
        updated_count = 0

        for data in dummy_crops:
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

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Dummy data import complete.\n"
            f"   Created: {created_count}\n"
            f"   Updated: {updated_count}\n"
            f"   Total crops in DB: {CropKnowledgeBase.objects.count()}"
        ))