from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit', 'title', 'phone')
    list_filter = ('unit', 'language')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
