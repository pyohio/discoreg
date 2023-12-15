from django.contrib import admin
import pytz

from .models import SessionNotification
import pytz


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("send_by_local_time", "sent", "title")

    # formfield_overrides = {
    #     models.TextField: {"widget": admin.widgets.AdminTextareaWidget}
    # }
    def send_by_local_time(self, obj):
        local_time = obj.send_by.astimezone(pytz.timezone("US/Eastern"))
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in [
            "description",
            "field_1_value",
            "field_2_value",
            "field_3_value",
        ]:
            kwargs["widget"] = admin.widgets.AdminTextareaWidget
        return super().formfield_for_dbfield(db_field, **kwargs)


admin.site.register(SessionNotification, NotificationAdmin)
