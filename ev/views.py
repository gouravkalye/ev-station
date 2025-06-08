from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Station, UserProfile, ChargingSession, UserPreferences, VehicleSegment, State
import random
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
from celery import shared_task
from django.utils import timezone
from decimal import Decimal


@login_required(login_url='/login/')
def home(request):
    # Get recently used stations (last 5)
    recent_stations = Station.objects.filter(
        chargingsession__user=request.user
    ).order_by('-chargingsession__start_time').distinct()[:5]

    # If no recent stations, show 5 random stations
    if not recent_stations:
        recent_stations = Station.objects.order_by('?')[:5]

    return render(request, 'ev/home.html', {
        'stations': recent_stations,
    })

def station(request):
    state = request.GET.get("state", "")
    city = request.GET.get("city", "")

    # Fetch all stations
    stations = Station.objects.all()

    # Apply filters if selected
    if state:
        stations = stations.filter(state__iexact=state)
    if city:
        stations = stations.filter(city__iexact=city)

    # Get all distinct states
    states = Station.objects.values_list("state", flat=True).distinct()

    # Get distinct cities
    if state:
        cities = list(Station.objects.filter(state__iexact=state).values_list("city", flat=True).distinct())
    else:
        cities = []

    context = {
        "stations": stations,
        "states": states,
        "cities": cities,
        "selected_state": state,
        "selected_city": city,
    }
    return render(request, "ev/station.html", context)

# Create your views here.

def get_server_time(request):
    now = datetime.now()  # ✅ Get current time
    return JsonResponse({"server_time": now.strftime("%Y-%m-%d %H:%M:%S")})  # ✅ Return formatted time

def server_info(request):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ Get formatted server time
    # Generate random CPU temperature between 30-80     
    voltage_info = random.uniform(110.0, 115.0)
    current_info = random.uniform(30.0, 80.0)
    return JsonResponse({
        "server_time": now, 
        "voltage_info": round(voltage_info, 1),
        "current_info": round(current_info, 1),
        # Round to 1 decimal place
    })

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'ev/register.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Change 'home' to your dashboard page
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'ev/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def ev_station_list(request):
    state = request.GET.get("state", "")
    city = request.GET.get("city", "")

    # Fetch all EV stations
    stations = Station.objects.all()

    # Apply filters if selected
    if state:
        stations = stations.filter(state__iexact=state)
    if city:
        stations = stations.filter(city__iexact=city)

    # Get all distinct states
    states = Station.objects.values_list("state", flat=True).distinct()

    # Get distinct cities
    if state:
        cities = list(Station.objects.filter(state__iexact=state).values_list("city", flat=True).distinct())
    else:
        cities = list(Station.objects.values_list("city", flat=True).distinct())

    print(f"Selected state: {state}, Cities: {cities}")  # Debugging

    return render(request, "ev/station.html", {
        "stations": stations,
        "states": states,
        "cities": cities,  # Now dynamically updates
        "selected_state": state,
        "selected_city": city,
    })

# API to fetch cities dynamically
def get_cities(request):
    state = request.GET.get("state", "")
    if state:
        cities = list(Station.objects.filter(state__iexact=state).values_list("city", flat=True).distinct())
    else:
        cities = []
    
    return JsonResponse({"cities": cities})

@login_required
def user_profile(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get recent charging sessions
    recent_sessions = ChargingSession.objects.filter(user=request.user).order_by('-start_time')[:5]
    
    # Get the most recent station used
    recent_station = None
    if recent_sessions.exists():
        recent_station = recent_sessions.first().station
    
    context = {
        'profile': profile,
        'recent_sessions': recent_sessions,
        'recent_station': recent_station,
    }
    return render(request, 'ev/user.html', context)

@login_required
@require_POST
def update_profile(request):
    profile = request.user.profile
    profile.save()
    messages.success(request, 'Profile updated successfully!')
    return redirect('user_profile')

@login_required
@require_POST
def update_preferences(request):
    preferences = request.user.preferences
    preferences.preferred_station_type = request.POST.get('preferred_station_type', 'BOTH')
    preferences.low_balance_alert = Decimal(request.POST.get('low_balance_alert', 20.00))
    preferences.save()
    messages.success(request, 'Preferences updated successfully!')
    return redirect('user_profile')

@login_required
def recharge_account(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                messages.error(request, 'Please enter a valid amount greater than 0')
                return redirect('recharge_account')
            
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Update balance
            profile.account_balance += amount
            profile.save()
            
            messages.success(request, f'Successfully recharged ₹{amount:.2f}')
            return redirect('user_profile')
            
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered')
            return redirect('recharge_account')
    
    return render(request, 'ev/recharge_account.html')

@login_required
def start_charging(request, station_id):
    try:
        station = Station.objects.get(id=station_id, is_available=True)
        profile = request.user.profile
        
        # Check if user has sufficient balance
        if profile.account_balance < Decimal('10.00'):
            messages.error(request, 'Insufficient balance. Please recharge your account.')
            return redirect('station')
        
        # Create new charging session
        session = ChargingSession.objects.create(
            user=request.user,
            station=station,
            start_time=timezone.now()
        )
        
        # Update station availability
        station.is_available = False
        station.save()
        
        messages.success(request, f'Charging started at {station.name}')
        return redirect('home')
        
    except Station.DoesNotExist:
        messages.error(request, 'Station not available')
        return redirect('station')

@login_required
def stop_charging(request, session_id):
    try:
        session = ChargingSession.objects.get(id=session_id, user=request.user, status='in_progress')
        profile = request.user.profile
        
        # Calculate energy consumed and cost
        duration = session.duration()
        hours = duration.total_seconds() / 3600
        energy_consumed = Decimal(str(hours * 7.2))  # Assuming 7.2kW charging rate
        cost = energy_consumed * Decimal('0.15')  # Assuming $0.15 per kWh
        
        # Update session
        session.end_time = timezone.now()
        session.energy_consumed = energy_consumed
        session.cost = cost
        session.status = 'completed'
        session.save()
        
        # Update station availability
        session.station.is_available = True
        session.station.save()
        
        # Update user profile
        profile.account_balance -= cost
        profile.total_sessions += 1
        profile.total_energy_consumed += energy_consumed
        profile.total_amount_spent += cost
        profile.save()
        
        messages.success(request, f'Charging completed. Energy consumed: {energy_consumed:.2f} kWh, Cost: ${cost:.2f}')
        return redirect('user_profile')
        
    except ChargingSession.DoesNotExist:
        messages.error(request, 'Invalid charging session')
        return redirect('user_profile')

@csrf_exempt
@require_POST
def update_charging_status(request):
    try:
        data = json.loads(request.body)
        station_id = data.get('station_id')
        station_name = data.get('station_name')
        station_location = data.get('station_location')
        is_charging = data.get('is_charging')
        
        # Here you would typically update your database
        # For now, we'll just return a success response
        response_data = {
            'status': 'success',
            'message': f'Charging status updated for {station_name}',
            'data': {
                'station_id': station_id,
                'station_name': station_name,
                'station_location': station_location,
                'is_charging': is_charging
            }
        }
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def test_api(request):
    stations = Station.objects.all().order_by('name')
    return render(request, 'ev/test_api.html', {'stations': stations})


@login_required
def start_charging(request, station_id):
    try:
        station = Station.objects.get(id=station_id, is_available=True)
        profile = request.user.profile
        
        # Check if user has sufficient balance
        if profile.account_balance < Decimal('10.00'):
            messages.error(request, 'Insufficient balance. Please recharge your account.')
            return redirect('station')
        
        # Create new charging session
        session = ChargingSession.objects.create(
            user=request.user,
            station=station,
            start_time=timezone.now(),
            status='in_progress'
        )
        
        # Update station availability
        station.is_available = False
        station.save()
        
        # Start Celery task
        handle_charging_session.delay(session.id)
        
        messages.success(request, f'Charging started at {station.name}')
        return redirect('home')
        
    except Station.DoesNotExist:
        messages.error(request, 'Station not available')
        return redirect('station')
    
@login_required
def stop_charging(request, session_id):
    try:
        session = ChargingSession.objects.get(id=session_id, user=request.user, status='in_progress')
        stop_charging_session.delay(session.id)
        messages.success(request, 'Charging session stopped successfully')
        return redirect('user_profile')
    except ChargingSession.DoesNotExist:
        messages.error(request, 'Charging session not found')
        return redirect('user_profile')
    
@csrf_exempt
@require_POST
def charging_api(request):
    try:
        data = json.loads(request.body)
        action = data.get('action')
        session_id = data.get('session_id')

        if action == 'start':
            station_id = data.get('station_id')
            response_data = start_charging(request, station_id)
            return JsonResponse(response_data)  # This must be a dict
        elif action == 'stop':
            stop_charging_session.delay(session_id)
            return JsonResponse({'status': 'success', 'message': 'Charging stopped'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def calculator_home(request):
    return render(request, 'ev/calculator_home.html')

def home_charging_calculator(request):
    vehicle_segments = VehicleSegment.objects.all()
    states = State.objects.all()
    context = {
        'vehicle_segments': vehicle_segments,
        'states': states,
    }
    return render(request, 'ev/home_charging_calculator.html', context)

def public_charging_calculator(request):
    vehicle_segments = VehicleSegment.objects.all()
    context = {
        'vehicle_segments': vehicle_segments,
    }
    return render(request, 'ev/public_charging_calculator.html', context)

def ev_comparison_calculator(request):
    vehicle_segments = VehicleSegment.objects.all()
    states = State.objects.all()
    context = {
        'vehicle_segments': vehicle_segments,
        'states': states,
    }
    return render(request, 'ev/ev_comparison_calculator.html', context)

@require_POST
def calculate_home_charging(request):
    try:
        data = json.loads(request.body)
        vehicle_segment = VehicleSegment.objects.get(id=data['vehicle_segment'])
        state = State.objects.get(id=data['state'])
        battery_capacity = Decimal(str(data['battery_capacity']))  # Convert to string first
        distance = Decimal(str(data['distance']))  # Convert to string first
        
        # Calculate charging cost
        charging_cost = battery_capacity * state.domestic_tariff
        charging_time = battery_capacity / Decimal('7.2')  # Convert 7.2 to Decimal
        
        return JsonResponse({
            'success': True,
            'charging_cost': float(charging_cost),
            'charging_time': float(charging_time),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def calculate_public_charging(request):
    try:
        data = json.loads(request.body)
        vehicle_segment = VehicleSegment.objects.get(id=data['vehicle_segment'])
        battery_capacity = Decimal(data['battery_capacity'])
        charger_power = Decimal(data['charger_power'])
        cost_per_kwh = Decimal(data['cost_per_kwh'])
        
        # Calculate charging cost and time
        charging_cost = battery_capacity * cost_per_kwh
        charging_time = battery_capacity / charger_power
        
        return JsonResponse({
            'success': True,
            'charging_cost': float(charging_cost),
            'charging_time': float(charging_time),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def calculate_ev_comparison(request):
    try:
        data = json.loads(request.body)
        vehicle_segment = VehicleSegment.objects.get(id=data['vehicle_segment'])
        state = State.objects.get(id=data['state'])
        annual_distance = Decimal(data['annual_distance'])
        home_charging_percentage = Decimal(data['home_charging_percentage'])
        public_charging_percentage = Decimal(data['public_charging_percentage'])
        conventional_mileage = Decimal(data['conventional_mileage'])
        
        # Calculate costs
        total_energy_needed = (annual_distance / vehicle_segment.average_range) * vehicle_segment.battery_capacity
        home_charging_cost = (total_energy_needed * home_charging_percentage / 100) * state.domestic_tariff
        public_charging_cost = (total_energy_needed * public_charging_percentage / 100) * state.public_charging_cost
        
        # Calculate conventional fuel cost (assuming ₹100 per liter)
        fuel_cost = (annual_distance / conventional_mileage) * 100
        
        return JsonResponse({
            'success': True,
            'ev_total_cost': float(home_charging_cost + public_charging_cost),
            'conventional_cost': float(fuel_cost),
            'savings': float(fuel_cost - (home_charging_cost + public_charging_cost)),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def set_current_station(request):
    try:
        data = json.loads(request.body)
        station_id = data.get('station_id')
        
        # Get the station details
        station = Station.objects.get(id=station_id)
        
        response_data = {
            'status': 'success',
            'data': {
                'station_id': station.id,
                'station_name': station.name,
                'station_address': station.address,
                'station_city': station.city,
                'station_state': station.state,
                'is_available': station.is_available
            }
        }
        return JsonResponse(response_data)
        
    except Station.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Station not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@login_required
def get_recent_usage(request):
    try:
        # Get the last 5 charging sessions for the current user
        recent_sessions = ChargingSession.objects.filter(
            user=request.user
        ).order_by('-start_time')[:5]

        logs = []
        for session in recent_sessions:
            logs.append({
                'time': session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'energy': float(session.energy_consumed),
                'cost': float(session.cost)
            })

        return JsonResponse({
            'status': 'success',
            'logs': logs
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
