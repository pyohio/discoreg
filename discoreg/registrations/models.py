from django.db import models


class DiscordServer(models.Model):
    server_id = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DiscordRole(models.Model):
    discord_role_id = models.CharField(max_length=32)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmailRole(models.Model):
    email = models.EmailField()
    discord_roles = models.ManyToManyField(DiscordRole)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Registration(models.Model):
    email = models.ForeignKey(EmailRole, on_delete=models.CASCADE)
    reference_id = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

