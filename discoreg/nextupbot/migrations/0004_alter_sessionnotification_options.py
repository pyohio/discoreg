# Generated by Django 3.2.5 on 2021-07-31 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nextupbot", "0003_auto_20210730_0639"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sessionnotification",
            options={"ordering": ["send_by", "title"]},
        ),
    ]