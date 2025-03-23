from django.urls import path
from .views import home  # Import a view
from .views import get_server_time
from .views import server_info
from .views import register, user_login, user_logout

urlpatterns = [
    path('', home, name='home'),
    path("server-time/", get_server_time, name="server_time"),
    path("server-info/", server_info, name="server_info"),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/',user_logout, name='logout'),
]
