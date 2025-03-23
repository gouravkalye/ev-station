from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime
import psutil  # ✅ Import psutil to get CPU load



users = [
        {"name": "Gourav", "email": "john.doe@example.com", "phone": "+1 234 567 890", "address": "1234 Main St, Springfield, USA"},
        {"name": "vighnesh", "email": "alice.johnson@example.com", "phone": "+1 987 654 321", "address": "5678 Elm St, New York, USA"},
        {"name": "Bob Smith", "email": "bob.smith@example.com", "phone": "+1 543 210 987", "address": "9101 Oak St, Los Angeles, USA"},
        {"name": "Charlie Brown", "email": "charlie.brown@example.com", "phone": "+1 321 654 987", "address": "222 Maple St, Chicago, USA"},
        {"name": "David White", "email": "david.white@example.com", "phone": "+1 123 456 789", "address": "333 Birch St, Houston, USA"}
    ]


def home(request):
    index = int(request.GET.get('index', 0))
    index = max(0, min(index, len(users) - 1))  # Ensure index is within range
    user = users[index]

    context = {
        "user": user,
        "index": index,
        "prev_index": max(index - 1, 0),
        "next_index": min(index + 1, len(users) - 1),
        "is_first": index == 0,
        "is_last": index == len(users) - 1,
    }

    # Check if the request is AJAX or explicitly asks for JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        context = users[index]
        return JsonResponse(context, content_type="application/json")

    return render(request, "ev/home.html", context)
# Create your views here.

def get_server_time(request):
    now = datetime.now()  # ✅ Get current time
    return JsonResponse({"server_time": now.strftime("%Y-%m-%d %H:%M:%S")})  # ✅ Return formatted time

def server_info(request):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ Get formatted server time
    cpu_load = psutil.sensors_temperatures()  # ✅ Get CPU usage over 1 second
    
    return JsonResponse({"server_time": now, "cpu_load": cpu_load})