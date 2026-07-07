#!/usr/bin/env python
"""Script to insert crop configurations and activity rules"""

import os
import sys
import django

# Add the project root to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
django.setup()

# Now import Django models (AFTER django.setup())
from crops.models import CropTypeConfig, CropActivityRule


def insert_crop_configs():
    """Insert 15 common Nepali crops with different varieties, regions, and seasons"""
    
    crop_configs = [
        # ==================== PADDY (RICE) - धान ====================
        {
            'crop_name': 'Paddy',
            'variety': 'Basmati',
            'region': 'terai',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 10,
            'vegetative_start_day': 11, 'vegetative_end_day': 40,
            'flowering_start_day': 41, 'flowering_end_day': 60,
            'maturation_start_day': 61, 'maturation_end_day': 85,
            'harvest_start_day': 86, 'harvest_end_day': 120,
            'total_growing_days': 120
        },
        {
            'crop_name': 'Paddy',
            'variety': 'Mansuli',
            'region': 'terai',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 8,
            'vegetative_start_day': 9, 'vegetative_end_day': 35,
            'flowering_start_day': 36, 'flowering_end_day': 55,
            'maturation_start_day': 56, 'maturation_end_day': 80,
            'harvest_start_day': 81, 'harvest_end_day': 110,
            'total_growing_days': 110
        },
        {
            'crop_name': 'Paddy',
            'variety': 'Jumli Marshi',
            'region': 'hilly',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 12,
            'vegetative_start_day': 13, 'vegetative_end_day': 50,
            'flowering_start_day': 51, 'flowering_end_day': 75,
            'maturation_start_day': 76, 'maturation_end_day': 100,
            'harvest_start_day': 101, 'harvest_end_day': 135,
            'total_growing_days': 135
        },
        {
            'crop_name': 'Paddy',
            'variety': 'Local',
            'region': 'terai',
            'season': 'monsoon',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 30,
            'flowering_start_day': 31, 'flowering_end_day': 50,
            'maturation_start_day': 51, 'maturation_end_day': 70,
            'harvest_start_day': 71, 'harvest_end_day': 95,
            'total_growing_days': 95
        },
        
        # ==================== MAIZE (CORN) - मकै ====================
        {
            'crop_name': 'Maize',
            'variety': 'Hybrid',
            'region': 'terai',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 35,
            'flowering_start_day': 36, 'flowering_end_day': 55,
            'maturation_start_day': 56, 'maturation_end_day': 75,
            'harvest_start_day': 76, 'harvest_end_day': 95,
            'total_growing_days': 95
        },
        {
            'crop_name': 'Maize',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 8,
            'vegetative_start_day': 9, 'vegetative_end_day': 40,
            'flowering_start_day': 41, 'flowering_end_day': 65,
            'maturation_start_day': 66, 'maturation_end_day': 90,
            'harvest_start_day': 91, 'harvest_end_day': 115,
            'total_growing_days': 115
        },
        {
            'crop_name': 'Maize',
            'variety': 'Rampur Composite',
            'region': 'terai',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 6,
            'vegetative_start_day': 7, 'vegetative_end_day': 32,
            'flowering_start_day': 33, 'flowering_end_day': 52,
            'maturation_start_day': 53, 'maturation_end_day': 72,
            'harvest_start_day': 73, 'harvest_end_day': 90,
            'total_growing_days': 90
        },
        
        # ==================== WHEAT - गहुँ ====================
        {
            'crop_name': 'Wheat',
            'variety': 'Gautam',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 10,
            'vegetative_start_day': 11, 'vegetative_end_day': 50,
            'flowering_start_day': 51, 'flowering_end_day': 70,
            'maturation_start_day': 71, 'maturation_end_day': 95,
            'harvest_start_day': 96, 'harvest_end_day': 115,
            'total_growing_days': 115
        },
        {
            'crop_name': 'Wheat',
            'variety': 'Vijaya',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 8,
            'vegetative_start_day': 9, 'vegetative_end_day': 45,
            'flowering_start_day': 46, 'flowering_end_day': 65,
            'maturation_start_day': 66, 'maturation_end_day': 85,
            'harvest_start_day': 86, 'harvest_end_day': 105,
            'total_growing_days': 105
        },
        {
            'crop_name': 'Wheat',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 12,
            'vegetative_start_day': 13, 'vegetative_end_day': 55,
            'flowering_start_day': 56, 'flowering_end_day': 80,
            'maturation_start_day': 81, 'maturation_end_day': 105,
            'harvest_start_day': 106, 'harvest_end_day': 130,
            'total_growing_days': 130
        },
        
        # ==================== POTATO - आलु ====================
        {
            'crop_name': 'Potato',
            'variety': 'Kufri Jyoti',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 15,
            'vegetative_start_day': 16, 'vegetative_end_day': 40,
            'flowering_start_day': 41, 'flowering_end_day': 60,
            'maturation_start_day': 61, 'maturation_end_day': 85,
            'harvest_start_day': 86, 'harvest_end_day': 100,
            'total_growing_days': 100
        },
        {
            'crop_name': 'Potato',
            'variety': 'Kufri Sinduri',
            'region': 'hilly',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 18,
            'vegetative_start_day': 19, 'vegetative_end_day': 45,
            'flowering_start_day': 46, 'flowering_end_day': 65,
            'maturation_start_day': 66, 'maturation_end_day': 90,
            'harvest_start_day': 91, 'harvest_end_day': 110,
            'total_growing_days': 110
        },
        
        # ==================== MUSTARD - तोरी ====================
        {
            'crop_name': 'Mustard',
            'variety': 'Tori-2',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 30,
            'flowering_start_day': 31, 'flowering_end_day': 50,
            'maturation_start_day': 51, 'maturation_end_day': 75,
            'harvest_start_day': 76, 'harvest_end_day': 95,
            'total_growing_days': 95
        },
        {
            'crop_name': 'Mustard',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 8,
            'vegetative_start_day': 9, 'vegetative_end_day': 35,
            'flowering_start_day': 36, 'flowering_end_day': 55,
            'maturation_start_day': 56, 'maturation_end_day': 80,
            'harvest_start_day': 81, 'harvest_end_day': 100,
            'total_growing_days': 100
        },
        
        # ==================== LENTIL - दाल ====================
        {
            'crop_name': 'Lentil',
            'variety': 'Simal',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 35,
            'flowering_start_day': 36, 'flowering_end_day': 55,
            'maturation_start_day': 56, 'maturation_end_day': 80,
            'harvest_start_day': 81, 'harvest_end_day': 100,
            'total_growing_days': 100
        },
        {
            'crop_name': 'Lentil',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 9,
            'vegetative_start_day': 10, 'vegetative_end_day': 40,
            'flowering_start_day': 41, 'flowering_end_day': 60,
            'maturation_start_day': 61, 'maturation_end_day': 85,
            'harvest_start_day': 86, 'harvest_end_day': 105,
            'total_growing_days': 105
        },
        
        # ==================== MILLET - कोदो ====================
        {
            'crop_name': 'Millet',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 5,
            'vegetative_start_day': 6, 'vegetative_end_day': 30,
            'flowering_start_day': 31, 'flowering_end_day': 50,
            'maturation_start_day': 51, 'maturation_end_day': 75,
            'harvest_start_day': 76, 'harvest_end_day': 95,
            'total_growing_days': 95
        },
        {
            'crop_name': 'Millet',
            'variety': 'Kodo',
            'region': 'himalayan',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 6,
            'vegetative_start_day': 7, 'vegetative_end_day': 35,
            'flowering_start_day': 36, 'flowering_end_day': 55,
            'maturation_start_day': 56, 'maturation_end_day': 80,
            'harvest_start_day': 81, 'harvest_end_day': 100,
            'total_growing_days': 100
        },
        
        # ==================== BARLEY - जौ ====================
        {
            'crop_name': 'Barley',
            'variety': 'Local',
            'region': 'terai',
            'season': 'winter',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 40,
            'flowering_start_day': 41, 'flowering_end_day': 60,
            'maturation_start_day': 61, 'maturation_end_day': 85,
            'harvest_start_day': 86, 'harvest_end_day': 105,
            'total_growing_days': 105
        },
        {
            'crop_name': 'Barley',
            'variety': 'Himalayan',
            'region': 'himalayan',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 10,
            'vegetative_start_day': 11, 'vegetative_end_day': 45,
            'flowering_start_day': 46, 'flowering_end_day': 65,
            'maturation_start_day': 66, 'maturation_end_day': 90,
            'harvest_start_day': 91, 'harvest_end_day': 110,
            'total_growing_days': 110
        },
        
        # ==================== BUCKWHEAT - फापर ====================
        {
            'crop_name': 'Buckwheat',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'autumn',
            'germination_start_day': 0, 'germination_end_day': 5,
            'vegetative_start_day': 6, 'vegetative_end_day': 25,
            'flowering_start_day': 26, 'flowering_end_day': 45,
            'maturation_start_day': 46, 'maturation_end_day': 65,
            'harvest_start_day': 66, 'harvest_end_day': 80,
            'total_growing_days': 80
        },
        
        # ==================== SOYBEAN - भटमास ====================
        {
            'crop_name': 'Soybean',
            'variety': 'Hybrid',
            'region': 'terai',
            'season': 'summer',
            'germination_start_day': 0, 'germination_end_day': 7,
            'vegetative_start_day': 8, 'vegetative_end_day': 30,
            'flowering_start_day': 31, 'flowering_end_day': 50,
            'maturation_start_day': 51, 'maturation_end_day': 75,
            'harvest_start_day': 76, 'harvest_end_day': 95,
            'total_growing_days': 95
        },
        
        # ==================== SUGARCANE - उखु ====================
        {
            'crop_name': 'Sugarcane',
            'variety': 'Local',
            'region': 'terai',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 30,
            'vegetative_start_day': 31, 'vegetative_end_day': 180,
            'flowering_start_day': 181, 'flowering_end_day': 240,
            'maturation_start_day': 241, 'maturation_end_day': 300,
            'harvest_start_day': 301, 'harvest_end_day': 365,
            'total_growing_days': 365
        },
        
        # ==================== GINGER - अदुवा ====================
        {
            'crop_name': 'Ginger',
            'variety': 'Local',
            'region': 'hilly',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 30,
            'vegetative_start_day': 31, 'vegetative_end_day': 90,
            'flowering_start_day': 91, 'flowering_end_day': 120,
            'maturation_start_day': 121, 'maturation_end_day': 180,
            'harvest_start_day': 181, 'harvest_end_day': 210,
            'total_growing_days': 210
        },
        
        # ==================== TURMERIC - बेसार ====================
        {
            'crop_name': 'Turmeric',
            'variety': 'Local',
            'region': 'terai',
            'season': 'spring',
            'germination_start_day': 0, 'germination_end_day': 25,
            'vegetative_start_day': 26, 'vegetative_end_day': 100,
            'flowering_start_day': 101, 'flowering_end_day': 130,
            'maturation_start_day': 131, 'maturation_end_day': 190,
            'harvest_start_day': 191, 'harvest_end_day': 220,
            'total_growing_days': 220
        },
    ]
    
    created_count = 0
    skipped_count = 0
    
    for config_data in crop_configs:
        try:
            obj, created = CropTypeConfig.objects.get_or_create(
                crop_name=config_data['crop_name'],
                variety=config_data['variety'],
                region=config_data['region'],
                season=config_data['season'],
                defaults=config_data
            )
            if created:
                created_count += 1
                print(f"✅ Created: {obj.get_display_name()}")
            else:
                skipped_count += 1
                print(f"⏭️ Already exists: {obj.get_display_name()}")
        except Exception as e:
            print(f"❌ Error creating {config_data['crop_name']} - {config_data['variety']}: {e}")
    
    print("\n" + "="*50)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Created: {created_count} new configurations")
    print(f"   ⏭️ Skipped: {skipped_count} existing configurations")
    print(f"   📦 Total in DB: {CropTypeConfig.objects.count()}")
    print("="*50)


def insert_activity_rules():
    """Insert crop-specific activity rules for different crops (POST-PLANTING ONLY - NO FIELD PREP)"""
    
    # Get all crop configs
    configs = CropTypeConfig.objects.filter(is_active=True)
    
    activities = []
    
    for config in configs:
        crop_name = config.crop_name
        
        # ==================== PADDY (RICE) SPECIFIC ACTIVITIES ====================
        if crop_name == 'Paddy':
            activities.extend([
                # Vegetative Stage (Post-planting) - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Apply Basal Fertilizer',
                    'description': 'Apply fertilizer after transplanting',
                    'measurements': 'Urea: 4.8 Kg/Ropani, DAP: 3.12 Kg/Ropani, Potash: 2.5 Kg/Ropani',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea during active tillering',
                    'measurements': 'Urea: 2.4 Kg/Ropani',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Weeding',
                    'description': 'Remove weeds to reduce competition',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation Management',
                    'description': 'Maintain proper water level in field',
                    'measurements': 'Keep 2-3 cm water',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Check for pests and diseases',
                    'measurements': '',
                    'target_pest': 'Rice Borer, Leaf folder, Gall midge',
                    'day_offset': 5,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at panicle initiation',
                    'measurements': 'Urea: 2.4 Kg/Ropani',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control pests during flowering',
                    'measurements': '',
                    'target_pest': 'Mealy bug, Sheath blight, Rice Hispa',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Weeding',
                    'description': 'Remove remaining weeds',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Spray',
                    'description': 'Apply micronutrients for better grain filling',
                    'measurements': 'ZnSO4: 0.5%, FeSO4: 0.5%',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Water Management',
                    'description': 'Maintain shallow water level during flowering',
                    'measurements': 'Keep 5-7 cm water',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Reduce Irrigation',
                    'description': 'Start draining water for grain filling',
                    'measurements': 'Stop irrigation 10-15 days before harvest',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Final Pest Check',
                    'description': 'Monitor for grain feeding insects',
                    'measurements': '',
                    'target_pest': 'Rice Gaundhi Bug',
                    'day_offset': 10,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Fungal Disease Control',
                    'description': 'Apply fungicide for grain discoloration',
                    'measurements': '',
                    'target_pest': 'Grain discoloration, False smut',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Nutrient Management',
                    'description': 'Apply potassium for better grain quality',
                    'measurements': 'Potash: 1.5 Kg/Ropani',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Field Draining',
                    'description': 'Drain field completely for uniform ripening',
                    'measurements': 'Complete drainage 7 days before harvest',
                    'target_pest': '',
                    'day_offset': 12,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Paddy',
                    'description': 'Harvest when 80-85% grains are straw colored',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest on dry sunny day for better quality',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Post Harvest Management',
                    'description': 'Proper drying and storage',
                    'measurements': 'Dry to 14% moisture content',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Separate grains from straw',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Winnowing',
                    'description': 'Clean grains for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage Pest Control',
                    'description': 'Apply safe storage measures',
                    'measurements': '',
                    'target_pest': 'Rice weevil, Grain moth',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== MAIZE SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Maize':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Basal Fertilizer Application',
                    'description': 'Apply fertilizer at sowing',
                    'measurements': 'DAP: 60 kg/hectare, Potash: 40 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea at knee height stage',
                    'measurements': 'Urea: 80 kg/hectare',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding and Earthing Up',
                    'description': 'Remove weeds and earth up soil',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Check for stem borer',
                    'measurements': '',
                    'target_pest': 'Maize Stem Borer, Armyworm, Cutworm',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'First irrigation at 3-4 leaf stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at tasseling stage',
                    'measurements': 'Urea: 40 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control pests during flowering',
                    'measurements': '',
                    'target_pest': 'Maize Cob Borer, Sap-sucking insects',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation',
                    'description': 'Critical irrigation during flowering',
                    'measurements': 'Irrigate at 50% tasseling and 50% silking',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control leaf diseases',
                    'measurements': '',
                    'target_pest': 'Maize leaf blight, Rust',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients',
                    'measurements': 'ZnSO4: 0.5%',
                    'target_pest': '',
                    'day_offset': 4,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Irrigation Management',
                    'description': 'Reduce water for grain filling',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Monitoring',
                    'description': 'Check for storage pests in field',
                    'measurements': '',
                    'target_pest': 'Maize weevil, Angoumois grain moth',
                    'day_offset': 7,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Control',
                    'description': 'Control ear rot diseases',
                    'measurements': '',
                    'target_pest': 'Fusarium ear rot, Aspergillus ear rot',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Nutrient Management',
                    'description': 'Apply Potassium for grain quality',
                    'measurements': 'Potash: 30 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Soil Moisture Management',
                    'description': 'Maintain adequate moisture for grain filling',
                    'measurements': 'Irrigate if soil moisture is low',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Maize',
                    'description': 'Harvest when husk turns brown and grains are hard',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 20-25% moisture content',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Post Harvest Drying',
                    'description': 'Dry ears for storage',
                    'measurements': 'Dry to 14% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Shelling',
                    'description': 'Remove grains from cob',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Grading',
                    'description': 'Sort grains by quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in clean, dry conditions',
                    'measurements': '',
                    'target_pest': 'Maize weevil, Rust-red flour beetle',
                    'day_offset': 4,
                    'order': 5
                },
            ])
        
        # ==================== WHEAT SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Wheat':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Basal Fertilizer',
                    'description': 'Apply DAP and Potash at sowing',
                    'measurements': 'DAP: 60 kg/hectare, Potash: 40 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Irrigation',
                    'description': 'First irrigation at crown root initiation',
                    'measurements': '21-25 days after sowing',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea at tillering stage',
                    'measurements': 'Urea: 60 kg/hectare',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Control broadleaf and grass weeds',
                    'measurements': '',
                    'target_pest': 'Wild oats, Chenopodium, Phalaris minor',
                    'day_offset': 12,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Second Irrigation',
                    'description': 'Irrigation at late tillering stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at booting stage',
                    'measurements': 'Urea: 40 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control rust and blight diseases',
                    'measurements': '',
                    'target_pest': 'Yellow rust, Brown rust, Leaf blight',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Third Irrigation',
                    'description': 'Critical irrigation at heading',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and armyworm',
                    'measurements': '',
                    'target_pest': 'Aphids, Armyworm, Hesseian fly',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients for grain filling',
                    'measurements': 'ZnSO4: 0.5%, FeSO4: 0.5%',
                    'target_pest': '',
                    'day_offset': 4,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Final Irrigation',
                    'description': 'Last irrigation before harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for late season diseases',
                    'measurements': '',
                    'target_pest': 'Karnal bunt, Flag smut',
                    'day_offset': 7,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop irrigation 10-12 days before harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Manage lodging in case of heavy rain/wind',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Check',
                    'description': 'Monitor grain quality parameters',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Wheat',
                    'description': 'Harvest when grains are hard and straw turns yellow',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 18-20% moisture content',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Separate grain from straw',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Winnowing and Cleaning',
                    'description': 'Clean grain for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry grain to safe moisture level',
                    'measurements': 'Dry to 12-14% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Wheat weevil, Lesser grain borer',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== POTATO SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Potato':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 100:50:80 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Earthing Up',
                    'description': 'First earthing up at 20-25 days',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'Maintain adequate soil moisture',
                    'measurements': 'Irrigate at 50% depletion',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Remove weeds to reduce competition',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Disease Monitoring',
                    'description': 'Monitor for early blight',
                    'measurements': '',
                    'target_pest': 'Early blight, Black leg',
                    'day_offset': 3,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Earthing Up',
                    'description': 'Second earthing up at flowering',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Late Blight Control',
                    'description': 'Spray fungicide for late blight',
                    'measurements': 'Ridomil 2g/liter water',
                    'target_pest': 'Late blight, Early blight',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Fertilizer Application',
                    'description': 'Apply potassium for tuber development',
                    'measurements': 'Potash: 80 kg/hectare',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and tuber moths',
                    'measurements': '',
                    'target_pest': 'Aphids, Potato tuber moth',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation',
                    'description': 'Critical irrigation during tuberization',
                    'measurements': 'Irrigate weekly',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering 2 weeks before harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Late Blight Control',
                    'description': 'Apply protective fungicide',
                    'measurements': '',
                    'target_pest': 'Late blight',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Vine Killing',
                    'description': 'Desiccate vines for uniform tuber maturation',
                    'measurements': 'Spray contact herbicide if needed',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Check',
                    'description': 'Monitor for storage diseases in field',
                    'measurements': '',
                    'target_pest': 'Soft rot, Wart disease',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Tuber Quality Assessment',
                    'description': 'Check tuber size and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Potato',
                    'description': 'Harvest when vines dry completely',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest on sunny day, cure for 10-14 days',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Curing',
                    'description': 'Cure potatoes for storage',
                    'measurements': '12-15°C, 90% humidity for 10-14 days',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Grading',
                    'description': 'Sort potatoes by size and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in cold storage',
                    'measurements': '2-4°C for processing, 8-10°C for seed',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage Monitoring',
                    'description': 'Monitor for sprouting and diseases',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 5
                },
            ])
        
        # ==================== MUSTARD SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Mustard':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:40:30 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Irrigation',
                    'description': 'Irrigate at rosette stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Remove weeds at rosette stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Thinning',
                    'description': 'Maintain proper plant spacing',
                    'measurements': 'Keep 15-20 cm plant spacing',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for aphids and flea beetles',
                    'measurements': '',
                    'target_pest': 'Aphids, Flea beetles, Sawfly',
                    'day_offset': 3,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and painted bug',
                    'measurements': '',
                    'target_pest': 'Mustard aphid, Painted bug',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Irrigation',
                    'description': 'Irrigate during peak flowering',
                    'measurements': 'Critical irrigation at flowering stage',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Spray',
                    'description': 'Apply boron for pod setting',
                    'measurements': 'Borax 0.2% solution',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control white rust and Alternaria blight',
                    'measurements': '',
                    'target_pest': 'White rust, Alternaria blight',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Nutrition',
                    'description': 'Apply sulfur for oil quality',
                    'measurements': 'Sulfur: 20 kg/hectare',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering at pod formation',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control pod borers',
                    'measurements': '',
                    'target_pest': 'Pod borer, Pod weevil',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for Alternaria blight on pods',
                    'measurements': '',
                    'target_pest': 'Alternaria blight',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pre-Harvest Desiccation',
                    'description': 'Speed up uniform maturity if needed',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check oil content and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Mustard',
                    'description': 'Harvest when pods turn yellow',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest in morning to avoid shattering',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate seeds',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning',
                    'description': 'Clean seeds for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry seeds to safe moisture level',
                    'measurements': 'Dry to 8-9% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in clean, dry conditions',
                    'measurements': '',
                    'target_pest': 'Mustard weevil, Grain moth',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== LENTIL SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Lentil':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply DAP at sowing',
                    'measurements': 'DAP: 25 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Inoculation',
                    'description': 'Rhizobium inoculation for nitrogen fixation',
                    'measurements': 'Rhizobium leguminosarum culture',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'First weeding at 20-25 days',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'Irrigate if soil moisture is low',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for aphids and cutworms',
                    'measurements': '',
                    'target_pest': 'Aphids, Cutworms, Semilooper',
                    'day_offset': 5,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and pod borer',
                    'measurements': '',
                    'target_pest': 'Aphids, Pod borer, Gram caterpillar',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients for pod setting',
                    'measurements': 'ZnSO4: 0.5%, Borax: 0.2%',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control rust and powdery mildew',
                    'measurements': '',
                    'target_pest': 'Rust, Powdery mildew',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation',
                    'description': 'Critical irrigation during flowering',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Weeding',
                    'description': 'Second weeding if needed',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering for maturation',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control pod borer at maturity',
                    'measurements': '',
                    'target_pest': 'Pod borer, Bruchids',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for diseases on pods',
                    'measurements': '',
                    'target_pest': 'Ascochyta blight',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Prevent lodging due to heavy rain',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Monitor seed maturity and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Lentil',
                    'description': 'Harvest when pods turn brown',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest when 80% pods mature',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate seeds',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning',
                    'description': 'Clean seeds for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry seeds to safe moisture level',
                    'measurements': 'Dry to 12-14% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Bruchid beetles, Weevils',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== MILLET SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Millet':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 40:20:20 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'First weeding at 15-20 days',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Thinning',
                    'description': 'Maintain proper plant spacing',
                    'measurements': 'Keep 10-15 cm plant spacing',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for shoot fly and stem borer',
                    'measurements': '',
                    'target_pest': 'Shoot fly, Stem borer',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'Irrigate if soil moisture is low',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control shoot fly and stem borer',
                    'measurements': '',
                    'target_pest': 'Shoot fly, Stem borer, Midge',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Weeding',
                    'description': 'Remove weeds at flowering',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Fertilizer Application',
                    'description': 'Top dressing at panicle initiation',
                    'measurements': 'Urea: 20 kg/hectare',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control rust and smut diseases',
                    'measurements': '',
                    'target_pest': 'Rust, Smut, Leaf spot',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation',
                    'description': 'Irrigate during flowering',
                    'measurements': 'Critical irrigation at flowering',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering for grain filling',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control birds and grain pests',
                    'measurements': '',
                    'target_pest': 'Birds, Grain pests',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for diseases on heads',
                    'measurements': '',
                    'target_pest': 'Head mold, Ergot',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Prevent lodging in heavy rain',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check grain quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Millet',
                    'description': 'Harvest when grains are hard',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Cut heads when grains are mature',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate grains',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning',
                    'description': 'Clean grains for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry grains to safe moisture level',
                    'measurements': 'Dry to 12-14% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Storage weevils, Moths',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== BARLEY SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Barley':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:30:20 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Irrigation',
                    'description': 'Irrigate at tillering stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Control weeds at tillering stage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Second Irrigation',
                    'description': 'Irrigation at maximum tillering',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for aphids and armyworm',
                    'measurements': '',
                    'target_pest': 'Aphids, Armyworm',
                    'day_offset': 5,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation Management',
                    'description': 'Critical irrigation at heading',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Fertilizer Application',
                    'description': 'Top dressing at heading',
                    'measurements': 'Urea: 30 kg/hectare',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control rust and powdery mildew',
                    'measurements': '',
                    'target_pest': 'Rust, Powdery mildew, Scab',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and Hesseian fly',
                    'measurements': '',
                    'target_pest': 'Aphids, Hesseian fly',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients',
                    'measurements': 'ZnSO4: 0.5%, FeSO4: 0.5%',
                    'target_pest': '',
                    'day_offset': 4,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering for maturation',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Prevent lodging in heavy rain/wind',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for late season diseases',
                    'measurements': '',
                    'target_pest': 'Net blotch, Barley scab',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pre-Harvest Desiccation',
                    'description': 'Speed up uniform maturity if needed',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 7,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check malting quality parameters',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Barley',
                    'description': 'Harvest when grains are hard',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 18-20% moisture',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate grains',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning and Grading',
                    'description': 'Clean and grade barley',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry to safe moisture level',
                    'measurements': 'Dry to 13-14% moisture for malting',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Storage weevils, Grain beetles',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== BUCKWHEAT SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Buckwheat':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply compost',
                    'measurements': 'FYM: 5-6 tons/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Manual weeding',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Thinning',
                    'description': 'Maintain proper plant spacing',
                    'measurements': 'Keep 20-25 cm spacing',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'Irrigate if soil moisture is low',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for aphids and pests',
                    'measurements': '',
                    'target_pest': 'Aphids, Caterpillars',
                    'day_offset': 3,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Weeding',
                    'description': 'Manual weeding',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Fertilizer Application',
                    'description': 'Apply potassium at flowering',
                    'measurements': 'Potash: 20 kg/hectare',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids if needed',
                    'measurements': '',
                    'target_pest': 'Aphids',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control leaf spot and downy mildew',
                    'measurements': '',
                    'target_pest': 'Leaf spot, Downy mildew',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients for seed set',
                    'measurements': 'Borax: 0.2%, ZnSO4: 0.5%',
                    'target_pest': '',
                    'day_offset': 4,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering for maturation',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Prevent lodging in heavy rain/wind',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for diseases on seeds',
                    'measurements': '',
                    'target_pest': 'Gray mold, Leaf spot',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pre-Harvest Desiccation',
                    'description': 'Speed up uniform maturity',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check seed quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Buckwheat',
                    'description': 'Harvest when 75% seeds turn brown',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest in morning to reduce shattering',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate seeds',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning and Grading',
                    'description': 'Clean and grade seeds',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry seeds to safe moisture level',
                    'measurements': 'Dry to 12-14% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Storage weevils',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== SOYBEAN SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Soybean':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply DAP at sowing',
                    'measurements': 'DAP: 50 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Inoculation',
                    'description': 'Rhizobium inoculation for nitrogen fixation',
                    'measurements': 'Rhizobium japonicum culture',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'First weeding at 15-20 days',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 8,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Thinning',
                    'description': 'Maintain proper plant spacing',
                    'measurements': 'Keep 5-10 cm spacing',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for stem fly and defoliators',
                    'measurements': '',
                    'target_pest': 'Stem fly, Leaf miner, Girdle beetle',
                    'day_offset': 3,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control girdle beetle and caterpillars',
                    'measurements': '',
                    'target_pest': 'Girdle beetle, Tobacco caterpillar, Semilooper',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation',
                    'description': 'Critical irrigation at flowering',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Foliar Nutrition',
                    'description': 'Apply micronutrients for pod setting',
                    'measurements': 'ZnSO4: 0.5%, Borax: 0.2%',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control rust and bacterial blight',
                    'measurements': '',
                    'target_pest': 'Rust, Bacterial blight, Powdery mildew',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Weeding',
                    'description': 'Second weeding if needed',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering for maturation',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control pod borers',
                    'measurements': '',
                    'target_pest': 'Pod borer, Pod bugs',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Monitoring',
                    'description': 'Check for pod and seed diseases',
                    'measurements': '',
                    'target_pest': 'Pod blight, Seed rot',
                    'day_offset': 3,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Lodging Prevention',
                    'description': 'Prevent lodging due to heavy rain',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check seed maturity and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Soybean',
                    'description': 'Harvest when pods turn brown',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 14% moisture',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Threshing',
                    'description': 'Thresh to separate beans',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning and Grading',
                    'description': 'Clean and grade beans',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry beans to safe moisture level',
                    'measurements': 'Dry to 12-13% moisture',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Bruchids, Weevils',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== SUGARCANE SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Sugarcane':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 150:60:60 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Earthing Up',
                    'description': 'Earth up soil around plants',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 30,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Second Fertilizer Application',
                    'description': 'Apply Urea at tillering stage',
                    'measurements': 'Urea: 80 kg/hectare',
                    'target_pest': '',
                    'day_offset': 45,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Remove weeds to reduce competition',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 30,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Check for stem borer and scale insects',
                    'measurements': '',
                    'target_pest': 'Stem borer, Scale insects, Termites',
                    'day_offset': 10,
                    'order': 5
                },
                # Flowering Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control pests during flowering',
                    'measurements': '',
                    'target_pest': 'Stem borer, White grub, Early shoot borer',
                    'day_offset': 5,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation Management',
                    'description': 'Regular irrigation during grand growth',
                    'measurements': 'Irrigate every 7-10 days',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Third Fertilizer Application',
                    'description': 'Apply additional nitrogen',
                    'measurements': 'Urea: 40 kg/hectare',
                    'target_pest': '',
                    'day_offset': 15,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Disease Control',
                    'description': 'Control red rot and smut',
                    'measurements': '',
                    'target_pest': 'Red rot, Smut, Wilt',
                    'day_offset': 5,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Weeding',
                    'description': 'Remove weeds in inter-row spaces',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 10,
                    'order': 5
                },
                # Maturation Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Trash Mulching',
                    'description': 'Apply trash mulching to conserve moisture',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Reduce Irrigation',
                    'description': 'Reduce water to enhance sugar accumulation',
                    'measurements': 'Stop irrigation 2-3 weeks before harvest',
                    'target_pest': '',
                    'day_offset': 15,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Brix Testing',
                    'description': 'Test sugar content periodically',
                    'measurements': 'Target Brix > 20%',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control top borer and scale insects',
                    'measurements': '',
                    'target_pest': 'Top borer, Scale insects',
                    'day_offset': 10,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Monitor sucrose content and maturity',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Sugarcane',
                    'description': 'Harvest when sugar content is maximum',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 10-12 months age for maximum sucrose',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Post Harvest Management',
                    'description': 'Process or store harvested cane',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Process within 24-48 hours to prevent sucrose loss',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning and Transport',
                    'description': 'Clean and transport to factory',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Ratoon Management',
                    'description': 'Prepare for ratoon crop if planned',
                    'measurements': 'Apply fertilizer and irrigation to ratoon',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Seed Cane Selection',
                    'description': 'Select healthy canes for next season planting',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
            ])
        
        # ==================== GINGER SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Ginger':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 75:50:75 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Mulching',
                    'description': 'Apply organic mulch to conserve moisture',
                    'measurements': 'Green leaves 10-15 tons/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Manual weeding to reduce competition',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 20,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation Management',
                    'description': 'Maintain adequate moisture',
                    'measurements': 'Irrigate weekly in dry periods',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for shoot borer and nematodes',
                    'measurements': '',
                    'target_pest': 'Shoot borer, Nematodes, Aphids',
                    'day_offset': 5,
                    'order': 5
                },
                # Maturation Stage - 5 activities (Ginger has no distinct flowering stage for production)
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop water 1 month before harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Disease Control',
                    'description': 'Monitor for rhizome rot',
                    'measurements': '',
                    'target_pest': 'Rhizome rot, Leaf spot, Soft rot',
                    'day_offset': 10,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Second Fertilizer Application',
                    'description': 'Apply potassium for rhizome development',
                    'measurements': 'Potash: 30 kg/hectare',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control rhizome flies and pests',
                    'measurements': '',
                    'target_pest': 'Rhizome fly, Scale insects',
                    'day_offset': 8,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check rhizome quality and size',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Ginger',
                    'description': 'Harvest when leaves turn yellow',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest for seed at 8 months, for market at 10 months',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning',
                    'description': 'Clean rhizomes after harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Grading',
                    'description': 'Sort by size and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Curing',
                    'description': 'Cure rhizomes for storage',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Storage',
                    'description': 'Store in proper conditions',
                    'measurements': 'Store at 12-15°C, 60-70% humidity',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 5
                },
            ])
        
        # ==================== TURMERIC SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Turmeric':
            activities.extend([
                # Vegetative Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:40:60 kg/hectare',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Mulching and Earthing Up',
                    'description': 'Apply mulch and earth up soil',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding',
                    'description': 'Manual weeding',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 20,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation',
                    'description': 'Maintain adequate moisture',
                    'measurements': 'Irrigate weekly',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Monitor for shoot borer and aphids',
                    'measurements': '',
                    'target_pest': 'Shoot borer, Aphids, Leaf eating caterpillars',
                    'day_offset': 5,
                    'order': 5
                },
                # Maturation Stage - 5 activities (Turmeric has no distinct flowering stage for production)
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Leaf Spot Control',
                    'description': 'Control leaf spot disease',
                    'measurements': '',
                    'target_pest': 'Leaf spot, Rhizome rot',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering before harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 15,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Second Fertilizer Application',
                    'description': 'Apply potassium for rhizome development',
                    'measurements': 'Potash: 30 kg/hectare',
                    'target_pest': '',
                    'day_offset': 5,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Pest Control',
                    'description': 'Control rhizome pests',
                    'measurements': '',
                    'target_pest': 'Rhizome weevil, Scale insects',
                    'day_offset': 10,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Quality Assessment',
                    'description': 'Check curcumin content and quality',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 0,
                    'order': 5
                },
                # Harvest Stage - 5 activities
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Turmeric',
                    'description': 'Harvest when leaves dry completely',
                    'measurements': '',
                    'target_pest': '',
                    'recommendations': 'Harvest at 7-9 months for processing',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Cleaning',
                    'description': 'Clean rhizomes after harvest',
                    'measurements': '',
                    'target_pest': '',
                    'day_offset': 1,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Boiling',
                    'description': 'Boil rhizomes for curing',
                    'measurements': 'Boil for 45-60 minutes',
                    'target_pest': '',
                    'day_offset': 2,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Drying',
                    'description': 'Dry to safe moisture level',
                    'measurements': 'Dry to 8-10% moisture',
                    'target_pest': '',
                    'day_offset': 3,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Polishing and Storage',
                    'description': 'Polish and store in proper conditions',
                    'measurements': '',
                    'target_pest': 'Storage pests',
                    'day_offset': 5,
                    'order': 5
                },
            ])
    
    created_count = 0
    skipped_count = 0
    
    for activity in activities:
        try:
            obj, created = CropActivityRule.objects.get_or_create(
                crop_config=activity['crop_config'],
                growth_stage=activity['growth_stage'],
                title=activity['title'],
                defaults=activity
            )
            if created:
                created_count += 1
                print(f"✅ Created: {obj}")
            else:
                skipped_count += 1
        except Exception as e:
            print(f"❌ Error creating activity for {activity['crop_config'].crop_name}: {e}")
    
    print("\n" + "="*50)
    print(f"📊 ACTIVITY SUMMARY:")
    print(f"   ✅ Created: {created_count} new activities")
    print(f"   ⏭️ Skipped: {skipped_count} existing activities")
    print(f"   📦 Total in DB: {CropActivityRule.objects.count()}")
    print("="*50)

if __name__ == "__main__":
    print("🌾 Starting crop data insertion...")
    print("="*50)
    
    # Insert crop configurations
    insert_crop_configs()
    
    print("\n" + "🌱" * 30)
    
    # Insert activity rules
    insert_activity_rules()
    
    print("\n✅ Data insertion completed successfully!")