from django.contrib import admin

from .models import SessionNotification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('send_by', 'title')

admin.site.register(SessionNotification, NotificationAdmin)