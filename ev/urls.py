from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('station/', views.station, name='station'),
    path('profile/', views.user_profile, name='user_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-preferences/', views.update_preferences, name='update_preferences'),
    path('recharge/', views.recharge_account, name='recharge_account'),
    path('start-charging/<int:station_id>/', views.start_charging, name='start_charging'),
    path('stop-charging/<int:session_id>/', views.stop_charging, name='stop_charging'),
    path('get-cities/', views.get_cities, name='get_cities'),
    path('server-time/', views.get_server_time, name='server_time'),
    path('server-info/', views.server_info, name='server_info'),
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('api/update_charging_status/', views.update_charging_status, name='update_charging_status'),
    path('api/charging/', views.charging_api, name='charging_api'),
    path('api/set_current_station/', views.set_current_station, name='set_current_station'),
    path('api/get_recent_usage/', views.get_recent_usage, name='get_recent_usage'),
    path('test-api/', views.test_api, name='test_api'),
    
    # Calculator URLs
    path('calculator/', views.calculator_home, name='calculator_home'),
    path('calculator/home-charging/', views.home_charging_calculator, name='home_charging_calculator'),
    path('calculator/public-charging/', views.public_charging_calculator, name='public_charging_calculator'),
    path('calculator/ev-comparison/', views.ev_comparison_calculator, name='ev_comparison_calculator'),
    path('calculate-home-charging/', views.calculate_home_charging, name='calculate_home_charging'),
    path('calculate-public-charging/', views.calculate_public_charging, name='calculate_public_charging'),
    path('calculate-ev-comparison/', views.calculate_ev_comparison, name='calculate_ev_comparison'),
]
