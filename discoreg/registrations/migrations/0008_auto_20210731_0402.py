# Generated by Django 3.2.5 on 2021-07-31 04:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("registrations", "0007_auto_20200720_1631"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="emailrole",
            options={"ordering": ["email"]},
        ),
        migrations.AlterModelOptions(
            name="registration",
            options={"ordering": ["email"]},
        ),
    ]
