from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import psutil  # ✅ Import psutil to get CPU load

users = [
        {"usr": "Gourav", "email": "john.doe@example.com", "phone": "+1 234 567 890", "address": "1234 Main St, Springfield, USA"},
        {"usr": "vighnesh", "email": "alice.johnson@example.com", "phone": "+1 987 654 321", "address": "5678 Elm St, New York, USA"},
        {"usr": "Bob Smith", "email": "bob.smith@example.com", "phone": "+1 543 210 987", "address": "9101 Oak St, Los Angeles, USA"},
        {"usr": "Charlie Brown", "email": "charlie.brown@example.com", "phone": "+1 321 654 987", "address": "222 Maple St, Chicago, USA"},
        {"nausrme": "David White", "email": "david.white@example.com", "phone": "+1 123 456 789", "address": "333 Birch St, Houston, USA"}
    ]
ev_station = [
    {
        "station_name": "Solar-ev",
        "address": "Power house, Ratnagiri",
        "city": "Ratnagiri",
        "state": "Maharashtra",
        "available": "Yes"
    },
 {
        "station_name": "Solar-ev",
        "address": "Power house, Ratnagiri",
        "city": "Ratnagiri",
        "state": "Maharashtra",
        "available": "Yes"
},
]

@login_required(login_url='login')  # Redirect to login page if not authenticated
def home(request):
    
    index = int(request.GET.get('index', 0))
    # index = max(0, min(index, len(users) - 1))  # Ensure index is within range
    # usr = users[index]

    # context = {
    #     "usr": usr,
    #     "index": index,
    #     "prev_index": max(index - 1, 0),
    #     "next_index": min(index + 1, len(users) - 1),
    #     "is_first": index == 0,
    #     "is_last": index == len(users) - 1,
    # }

    # Check if the request is AJAX or explicitly asks for JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # context = ev_station[index]
        return JsonResponse(ev_station[0], content_type="application/json")

    return render(request, "ev/home.html", ev_station[0])


# Create your views here.

def get_server_time(request):
    now = datetime.now()  # ✅ Get current time
    return JsonResponse({"server_time": now.strftime("%Y-%m-%d %H:%M:%S")})  # ✅ Return formatted time

def server_info(request):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ Get formatted server time
    cpu_load = psutil.sensors_temperatures()  # ✅ Get CPU usage over 1 second
    
    return JsonResponse({"server_time": now, "cpu_load": cpu_load})


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
                return redirect('ev/login')
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