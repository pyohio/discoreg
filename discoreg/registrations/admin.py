from django.contrib import admin

from .models import DiscordRole, DiscordServer, EmailRole, Registration

admin.site.register(DiscordRole)
admin.site.register(DiscordServer)
admin.site.register(EmailRole)
admin.site.register(Registration)
