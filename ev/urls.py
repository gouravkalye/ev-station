from django.urls import path
from .views import home  # Import a view
from .views import get_server_time
from .views import server_info

urlpatterns = [
    path('', home, name='home'),
    path("server-time/", get_server_time, name="server_time"),
    path("server-info/", server_info, name="server_info"),
]
