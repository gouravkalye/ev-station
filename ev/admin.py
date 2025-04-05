from django.contrib import admin
from .models import Station, UserProfile, ChargingSession, UserPreferences

admin.site.site_header = "EV Charger Management"
admin.site.site_title = "EV Admin Portal"
admin.site.index_title = "Welcome to EV Station Dashboard"

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_available")
    search_fields = ("name", "city", "state")
    list_filter = ("city", "state", "is_available")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "account_balance", "total_sessions")
    search_fields = ("user__username", "user__email")

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "preferred_station_type", "low_balance_alert")
    search_fields = ("user__username",)

@admin.register(ChargingSession)
class ChargingSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "station", "start_time", "status")
    search_fields = ("user__username", "station__name")
    list_filter = ("status",)
