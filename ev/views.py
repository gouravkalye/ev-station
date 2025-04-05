from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import EvStation
import random


@login_required(login_url='login')  # Redirect to login page if not authenticated
def home(request):
    # Check if the request is AJAX or explicitly asks for JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        ev_stations = EvStation.objects.all().values("name", "address", "city", "state", "zip_code")
        return JsonResponse(list(ev_stations), safe=False)  # Convert QuerySet to list

    # For normal page rendering
    ev_stations = list(EvStation.objects.all())
    station = ev_stations[0]
    return render(request, "ev/home.html", {"stations": station})

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
    stations = EvStation.objects.all()

    # Apply filters if selected
    if state:
        stations = stations.filter(state__iexact=state)
    if city:
        stations = stations.filter(city__iexact=city)

    # Get all distinct states
    states = EvStation.objects.values_list("state", flat=True).distinct()

    # Get distinct cities
    if state:
        cities = list(EvStation.objects.filter(state__iexact=state).values_list("city", flat=True).distinct())
    else:
        cities = list(EvStation.objects.values_list("city", flat=True).distinct())

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
        cities = list(EvStation.objects.filter(state__iexact=state).values_list("city", flat=True).distinct())
    else:
        cities = []
    
    return JsonResponse({"cities": cities})

@login_required(login_url='login')
def user_profile(request):
    # Get user's charging sessions (you'll need to implement this model later)
    charging_sessions = []  # Placeholder for now
    
    # Calculate statistics (placeholder values for now)
    total_sessions = 25
    total_energy = 250
    total_spent = 125.50
    
    return render(request, 'ev/user.html', {
        'user': request.user,
        'charging_sessions': charging_sessions,
        'total_sessions': total_sessions,
        'total_energy': total_energy,
        'total_spent': total_spent
    })