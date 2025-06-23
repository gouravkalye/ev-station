from django.db import migrations

def add_seed_data(apps, schema_editor):
    VehicleSegment = apps.get_model('ev', 'VehicleSegment')
    State = apps.get_model('ev', 'State')

    # Add vehicle segments
    vehicle_segments = [
        {
            'name': 'Compact EV',
            'average_range': 250,
            'battery_capacity': 30
        },
        {
            'name': 'Mid-size EV',
            'average_range': 400,
            'battery_capacity': 50
        },
        {
            'name': 'Luxury EV',
            'average_range': 500,
            'battery_capacity': 75
        },
        {
            'name': 'SUV EV',
            'average_range': 450,
            'battery_capacity': 85
        }
    ]

    for segment in vehicle_segments:
        VehicleSegment.objects.create(**segment)

    # Add states with tariffs
    states = [
        {
            'name': 'Maharashtra',
            'domestic_tariff': 7.5,
            'public_charging_cost': 12.0
        },
        {
            'name': 'Delhi',
            'domestic_tariff': 6.5,
            'public_charging_cost': 11.0
        },
        {
            'name': 'Karnataka',
            'domestic_tariff': 7.0,
            'public_charging_cost': 11.5
        },
        {
            'name': 'Tamil Nadu',
            'domestic_tariff': 6.8,
            'public_charging_cost': 12.0
        },
        {
            'name': 'Gujarat',
            'domestic_tariff': 7.2,
            'public_charging_cost': 11.8
        }
    ]

    for state in states:
        State.objects.create(**state)

def remove_seed_data(apps, schema_editor):
    VehicleSegment = apps.get_model('ev', 'VehicleSegment')
    State = apps.get_model('ev', 'State')
    
    VehicleSegment.objects.all().delete()
    State.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('ev', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_seed_data, remove_seed_data),
    ] 