from django.db import models


class DiscordServer(models.Model):
    name = models.CharField(max_length=32, blank=True)
    server_id = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.server_id}>"


class DiscordRole(models.Model):
    name = models.CharField(max_length=32, blank=True)
    discord_role_id = models.CharField(max_length=32)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)
    assign_by_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.discord_role_id}>"


class EmailRole(models.Model):
    email = models.EmailField(unique=True)
    discord_roles = models.ManyToManyField(DiscordRole, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discord_user_id = models.CharField(max_length=32, blank=True, null=True, default=None)

    def __str__(self):
        # role_names = [role.name for role in self.discord_roles.all()]
        return f"{self.email}"


class Registration(models.Model):
    reference_id = models.CharField(max_length=32)
    email = models.ForeignKey(EmailRole, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference_id} ({self.email.email})"
