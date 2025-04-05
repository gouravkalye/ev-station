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
    path('test-api/', views.test_api, name='test_api'),
]
