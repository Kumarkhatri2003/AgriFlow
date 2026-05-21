# Get the backend directory path
import os
import sys

import django


backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to path
sys.path.append(backend_dir)

# Set Django settings module - Try different possibilities
if os.path.exists(os.path.join(backend_dir, 'backend', 'settings.py')):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
elif os.path.exists(os.path.join(backend_dir, 'settings.py')):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
else:
    # Look for any settings file
    for root, dirs, files in os.walk(backend_dir):
        if 'settings.py' in files:
            settings_path = os.path.relpath(os.path.join(root, 'settings.py'), backend_dir)
            settings_module = settings_path.replace(os.sep, '.').replace('.py', '')
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
            break

# Initialize Django
django.setup()

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
    """Insert crop-specific activity rules for different crops"""
    
    # Get all crop configs
    configs = CropTypeConfig.objects.filter(is_active=True)
    
    activities = []
    
    for config in configs:
        crop_name = config.crop_name
        variety = config.variety
        region = config.region
        
        # ==================== PADDY (RICE) SPECIFIC ACTIVITIES ====================
        if crop_name == 'Paddy':
            activities.extend([
                # Germination Stage
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds with fungicide to prevent seed-borne diseases',
                    'measurements': 'Carbendazim 2g/kg seed or Thiram 3g/kg seed',
                    'target_pest': 'Blast, Bacterial leaf blight, Foot rot',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'First Ploughing',
                    'description': 'Prepare field with first ploughing',
                    'measurements': 'FYM: 250-300 Kg/Ropani',
                    'day_offset': 0,
                    'order': 2
                },
                # Vegetative Stage
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Apply Basal Fertilizer',
                    'description': 'Apply fertilizer before transplanting',
                    'measurements': 'Urea: 4.8 Kg/Ropani, DAP: 3.12 Kg/Ropani, Potash: 2.5 Kg/Ropani',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea during active tillering',
                    'measurements': 'Urea: 2.4 Kg/Ropani',
                    'day_offset': 10,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Weeding',
                    'description': 'Remove weeds to reduce competition',
                    'measurements': '',
                    'day_offset': 10,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Irrigation Management',
                    'description': 'Maintain proper water level in field',
                    'measurements': 'Keep 2-3 cm water',
                    'day_offset': 0,
                    'order': 4
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Check for pests and diseases',
                    'measurements': '',
                    'target_pest': 'Rice Borer, Leaf folder',
                    'day_offset': 5,
                    'order': 5
                },
                # Flowering Stage
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at panicle initiation',
                    'measurements': 'Urea: 2.4 Kg/Ropani',
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
                    'day_offset': 0,
                    'order': 3
                },
                # Maturation Stage
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Reduce Irrigation',
                    'description': 'Start draining water for grain filling',
                    'measurements': 'Stop irrigation 10-15 days before harvest',
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
                # Harvest Stage
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Paddy',
                    'description': 'Harvest when 80-85% grains are straw colored',
                    'measurements': '',
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
                    'day_offset': 0,
                    'order': 2
                },
            ])
        
        # ==================== MAIZE SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Maize':
            activities.extend([
                # Germination Stage
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds with fungicide and insecticide',
                    'measurements': 'Vitavax 2g/kg seed + Imidacloprid 1ml/kg seed',
                    'target_pest': 'Seed borne diseases, Termites',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Land Preparation',
                    'description': 'Prepare field with proper tilth',
                    'measurements': 'FYM: 10-12 tons/hectare',
                    'day_offset': 0,
                    'order': 2
                },
                # Vegetative Stage
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Basal Fertilizer Application',
                    'description': 'Apply fertilizer at sowing',
                    'measurements': 'DAP: 60 kg/hectare, Potash: 40 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea at knee height stage',
                    'measurements': 'Urea: 80 kg/hectare',
                    'day_offset': 8,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Weeding and Earthing Up',
                    'description': 'Remove weeds and earthing up soil',
                    'measurements': '',
                    'day_offset': 8,
                    'order': 3
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Pest Monitoring',
                    'description': 'Check for stem borer',
                    'measurements': '',
                    'target_pest': 'Maize Stem Borer, Armyworm',
                    'day_offset': 5,
                    'order': 4
                },
                # Flowering Stage
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at tasseling stage',
                    'measurements': 'Urea: 40 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control pests during flowering',
                    'measurements': '',
                    'target_pest': 'Maize Cob Borer',
                    'day_offset': 5,
                    'order': 2
                },
                # Maturation Stage
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Irrigation Management',
                    'description': 'Reduce water for grain filling',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                # Harvest Stage
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Maize',
                    'description': 'Harvest when husk turns brown and grains are hard',
                    'measurements': '',
                    'recommendations': 'Harvest at 20-25% moisture content',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== WHEAT SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Wheat':
            activities.extend([
                # Germination Stage
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds against smut and rust',
                    'measurements': 'Vitavax 2g/kg seed',
                    'target_pest': 'Loose smut, Flag smut',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Field Preparation',
                    'description': 'Proper land preparation for sowing',
                    'measurements': 'FYM: 8-10 tons/hectare',
                    'day_offset': 0,
                    'order': 2
                },
                # Vegetative Stage
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Basal Fertilizer',
                    'description': 'Apply DAP and Potash at sowing',
                    'measurements': 'DAP: 60 kg/hectare, Potash: 40 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Irrigation',
                    'description': 'First irrigation at crown root initiation',
                    'measurements': '21-25 days after sowing',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Top Dressing',
                    'description': 'Apply Urea at tillering stage',
                    'measurements': 'Urea: 60 kg/hectare',
                    'day_offset': 10,
                    'order': 3
                },
                # Flowering Stage
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Top Dressing',
                    'description': 'Apply Urea at booting stage',
                    'measurements': 'Urea: 40 kg/hectare',
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
                # Maturation Stage
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Final Irrigation',
                    'description': 'Last irrigation before harvest',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                # Harvest Stage
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Wheat',
                    'description': 'Harvest when grains are hard and straw turns yellow',
                    'measurements': '',
                    'recommendations': 'Harvest at 18-20% moisture content',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== POTATO SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Potato':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Tuber Treatment',
                    'description': 'Treat seed tubers before planting',
                    'measurements': 'Boric acid 1% for 15 minutes',
                    'target_pest': 'Late blight, Common scab',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Sprouting Treatment',
                    'description': 'Pre-sprouting of seed tubers',
                    'measurements': 'Store in diffused light for 15-20 days',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 100:50:80 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Earthing Up',
                    'description': 'First earthing up at 20-25 days',
                    'measurements': '',
                    'day_offset': 5,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Second Earthing Up',
                    'description': 'Second earthing up at flowering',
                    'measurements': '',
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
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering 2 weeks before harvest',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Potato',
                    'description': 'Harvest when vines dry completely',
                    'measurements': '',
                    'recommendations': 'Harvest on sunny day, cure for 10-14 days',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== MUSTARD SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Mustard':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds against Alternaria blight',
                    'measurements': 'Carbendazim 2g/kg seed',
                    'target_pest': 'Alternaria blight',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:40:30 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'First Irrigation',
                    'description': 'Irrigate at rosette stage',
                    'measurements': '',
                    'day_offset': 10,
                    'order': 2
                },
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
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop watering at pod formation',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Mustard',
                    'description': 'Harvest when pods turn yellow',
                    'measurements': '',
                    'recommendations': 'Harvest in morning to avoid shattering',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== LENTIL SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Lentil':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat with Rhizobium culture',
                    'measurements': 'Rhizobium leguminosarum 500g/10kg seed',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply DAP at sowing',
                    'measurements': 'DAP: 25 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control aphids and pod borer',
                    'measurements': '',
                    'target_pest': 'Aphids, Pod borer',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Lentil',
                    'description': 'Harvest when pods turn brown',
                    'measurements': '',
                    'recommendations': 'Harvest when 80% pods mature',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== MILLET SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Millet':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds for downy mildew',
                    'measurements': 'Metalaxyl 2g/kg seed',
                    'target_pest': 'Downy mildew',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 40:20:20 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control shoot fly and stem borer',
                    'measurements': '',
                    'target_pest': 'Shoot fly, Stem borer',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Millet',
                    'description': 'Harvest when grains are hard',
                    'measurements': '',
                    'recommendations': 'Cut heads when grains are mature',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== BARLEY SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Barley':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat seeds for smut',
                    'measurements': 'Vitavax 2g/kg seed',
                    'target_pest': 'Covered smut, Loose smut',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:30:20 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Irrigation Management',
                    'description': 'Critical irrigation at heading',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Barley',
                    'description': 'Harvest when grains are hard',
                    'measurements': '',
                    'recommendations': 'Harvest at 18-20% moisture',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== BUCKWHEAT SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Buckwheat':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'No chemical treatment needed for buckwheat',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply compost',
                    'measurements': 'FYM: 5-6 tons/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Weeding',
                    'description': 'Manual weeding',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Buckwheat',
                    'description': 'Harvest when 75% seeds turn brown',
                    'measurements': '',
                    'recommendations': 'Harvest in morning to reduce shattering',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== SOYBEAN SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Soybean':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat with Rhizobium and fungicide',
                    'measurements': 'Rhizobium japonicum + Carbendazim',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply DAP at sowing',
                    'measurements': 'DAP: 50 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'flowering',
                    'title': 'Pest Control',
                    'description': 'Control girdle beetle and caterpillars',
                    'measurements': '',
                    'target_pest': 'Girdle beetle, Tobacco caterpillar',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Soybean',
                    'description': 'Harvest when pods turn brown',
                    'measurements': '',
                    'recommendations': 'Harvest at 14% moisture',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== SUGARCANE SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Sugarcane':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Seed Treatment',
                    'description': 'Treat setts with fungicide',
                    'measurements': 'Carbendazim 1g/liter water',
                    'target_pest': 'Red rot, Smut',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 150:60:60 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Earthing Up',
                    'description': 'Earth up soil around plants',
                    'measurements': '',
                    'day_offset': 30,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Trash Mulching',
                    'description': 'Apply trash mulching',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Sugarcane',
                    'description': 'Harvest when sugar content is maximum',
                    'measurements': '',
                    'recommendations': 'Harvest at 10-12 months age',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== GINGER SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Ginger':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Rhizome Treatment',
                    'description': 'Treat rhizomes before planting',
                    'measurements': 'Carbendazim + Mancozeb 2g/liter for 30 min',
                    'target_pest': 'Rhizome rot',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 75:50:75 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Mulching',
                    'description': 'Apply organic mulch',
                    'measurements': 'Green leaves 10-15 tons/hectare',
                    'day_offset': 0,
                    'order': 2
                },
                {
                    'crop_config': config,
                    'growth_stage': 'maturation',
                    'title': 'Stop Irrigation',
                    'description': 'Stop water 1 month before harvest',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'harvest',
                    'title': 'Harvest Ginger',
                    'description': 'Harvest when leaves turn yellow',
                    'measurements': '',
                    'recommendations': 'Harvest for seed at 8 months, for market at 10 months',
                    'day_offset': 0,
                    'order': 1
                },
            ])
        
        # ==================== TURMERIC SPECIFIC ACTIVITIES ====================
        elif crop_name == 'Turmeric':
            activities.extend([
                {
                    'crop_config': config,
                    'growth_stage': 'germination',
                    'title': 'Rhizome Treatment',
                    'description': 'Treat rhizomes with fungicide',
                    'measurements': 'Mancozeb 3g/liter water for 30 min',
                    'target_pest': 'Rhizome rot, Leaf spot',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Fertilizer Application',
                    'description': 'Apply NPK fertilizer',
                    'measurements': 'N:P:K = 60:40:60 kg/hectare',
                    'day_offset': 0,
                    'order': 1
                },
                {
                    'crop_config': config,
                    'growth_stage': 'vegetative',
                    'title': 'Mulching and Earthing Up',
                    'description': 'Apply mulch and earth up',
                    'measurements': '',
                    'day_offset': 0,
                    'order': 2
                },
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
                    'growth_stage': 'harvest',
                    'title': 'Harvest Turmeric',
                    'description': 'Harvest when leaves dry completely',
                    'measurements': '',
                    'recommendations': 'Harvest at 7-9 months for processing',
                    'day_offset': 0,
                    'order': 1
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