from django.core.management.base import BaseCommand
from ev.models import Station
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with Indian EV charging stations'

    def handle(self, *args, **kwargs):
        # List of major Indian cities with their coordinates
        stations = [
            # Delhi NCR
            {
                'name': 'Tata Power - Connaught Place',
                'address': 'Block A, Connaught Place',
                'city': 'New Delhi',
                'state': 'Delhi',
                'zip_code': '110001',
                'gps_location': '28.6304,77.2177',
                'is_available': True
            },
            {
                'name': 'Fortum - Cyber Hub',
                'address': 'DLF Cyber City, Gurugram',
                'city': 'Gurugram',
                'state': 'Haryana',
                'zip_code': '122002',
                'gps_location': '28.4961,77.0943',
                'is_available': True
            },
            {
                'name': 'EVRE - Noida Sector 18',
                'address': 'Sector 18 Market',
                'city': 'Noida',
                'state': 'Uttar Pradesh',
                'zip_code': '201301',
                'gps_location': '28.5700,77.3217',
                'is_available': True
            },

            # Mumbai
            {
                'name': 'Tata Power - Bandra Kurla Complex',
                'address': 'BKC Complex, Bandra East',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'zip_code': '400051',
                'gps_location': '19.0662,72.8646',
                'is_available': True
            },
            {
                'name': 'Magenta - Powai',
                'address': 'Hiranandani Gardens',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'zip_code': '400076',
                'gps_location': '19.1197,72.9051',
                'is_available': False
            },

            # Bangalore
            {
                'name': 'Ather Grid - Koramangala',
                'address': '5th Block, Koramangala',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560034',
                'gps_location': '12.9352,77.6245',
                'is_available': True
            },
            {
                'name': 'ChargeZone - Whitefield',
                'address': 'ITPL Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560066',
                'gps_location': '12.9698,77.7499',
                'is_available': True
            },

            # Chennai
            {
                'name': 'Zeon - T Nagar',
                'address': 'Pondy Bazaar',
                'city': 'Chennai',
                'state': 'Tamil Nadu',
                'zip_code': '600017',
                'gps_location': '13.0399,80.2405',
                'is_available': True
            },
            {
                'name': 'EVRE - OMR',
                'address': 'OMR Road, Sholinganallur',
                'city': 'Chennai',
                'state': 'Tamil Nadu',
                'zip_code': '600119',
                'gps_location': '12.8996,80.2209',
                'is_available': False
            },

            # Hyderabad
            {
                'name': 'Tata Power - Hitech City',
                'address': 'Madhapur',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zip_code': '500081',
                'gps_location': '17.4474,78.3762',
                'is_available': True
            },
            {
                'name': 'ChargePoint - Banjara Hills',
                'address': 'Road No. 12',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zip_code': '500034',
                'gps_location': '17.4239,78.4318',
                'is_available': True
            },

            # Kolkata
            {
                'name': 'Fortum - Salt Lake',
                'address': 'Sector V',
                'city': 'Kolkata',
                'state': 'West Bengal',
                'zip_code': '700091',
                'gps_location': '22.5726,88.3639',
                'is_available': True
            },
            {
                'name': 'EVRE - Park Street',
                'address': 'Park Street Area',
                'city': 'Kolkata',
                'state': 'West Bengal',
                'zip_code': '700016',
                'gps_location': '22.5510,88.3529',
                'is_available': False
            },

            # Pune
            {
                'name': 'Tata Power - Koregaon Park',
                'address': 'North Main Road',
                'city': 'Pune',
                'state': 'Maharashtra',
                'zip_code': '411001',
                'gps_location': '18.5333,73.9000',
                'is_available': True
            },
            {
                'name': 'Magenta - Hinjewadi',
                'address': 'Rajiv Gandhi Infotech Park',
                'city': 'Pune',
                'state': 'Maharashtra',
                'zip_code': '411057',
                'gps_location': '18.5928,73.7349',
                'is_available': True
            },

            # Ahmedabad
            {
                'name': 'ChargeZone - Prahlad Nagar',
                'address': 'Prahlad Nagar Road',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'zip_code': '380015',
                'gps_location': '23.0225,72.5714',
                'is_available': True
            },
            {
                'name': 'EVRE - SG Highway',
                'address': 'Sarkhej-Gandhinagar Highway',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'zip_code': '380054',
                'gps_location': '23.0716,72.5210',
                'is_available': False
            }
        ]

        # Create stations
        for station_data in stations:
            Station.objects.get_or_create(
                name=station_data['name'],
                defaults=station_data
            )
            self.stdout.write(self.style.SUCCESS(f'Created station: {station_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Indian EV charging stations')) 