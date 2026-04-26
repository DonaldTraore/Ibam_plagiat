from django.contrib import admin
from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'entity_id', 'departement', 'created_at']
    list_filter = ['action', 'entity_type', 'departement', 'created_at']
    search_fields = ['details', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
