from django.db import models


class SessionNotification(models.Model):
    title = models.CharField(max_length=256)
    url = models.URLField(null=True, blank=True, default=None)
    description = models.CharField(max_length=2048, null=True, blank=True, default="")
    color_hex_string = models.CharField(max_length=6, default="ffffff")
    field_1_name = models.CharField(max_length=256, null=True, blank=True, default=None)
    field_1_value = models.CharField(
        max_length=1024, null=True, blank=True, default=None
    )
    field_2_name = models.CharField(max_length=256, null=True, blank=True, default=None)
    field_2_value = models.CharField(
        max_length=1024, null=True, blank=True, default=None
    )
    field_3_name = models.CharField(max_length=256, null=True, blank=True, default=None)
    field_3_value = models.CharField(
        max_length=1024, null=True, blank=True, default=None
    )
    author_name = models.CharField(
        max_length=256, default="Up next:", null=True, blank=True
    )
    author_email = models.EmailField(blank=True, default="")
    send_by = models.DateTimeField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ["send_by", "title"]
