from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'user', 'type', 'lu', 'email_envoye', 'created_at']
    list_filter = ['type', 'lu', 'email_envoye', 'created_at']
    search_fields = ['titre', 'message', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['date_lecture', 'date_envoi_email', 'created_at']
