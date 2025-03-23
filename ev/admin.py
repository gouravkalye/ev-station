from django.contrib import admin
from .models import EvStation
# Register your models here.

admin.site.site_header = "EV Charger Management"
admin.site.site_title = "EV Admin Portal"
admin.site.index_title = "Welcome to EV Station Dashboard"

@admin.register(EvStation)
class EvStationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_available")  # Show these fields in list view
    search_fields = ("name", "city", "state")  # Enable search
    list_filter = ("city", "state", "is_available")  # Enable filtering options
    ordering = ("name",)  # Order by name
