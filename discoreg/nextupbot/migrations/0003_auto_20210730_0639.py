# Generated by Django 3.2.4 on 2021-07-30 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nextupbot', '0002_auto_20200725_0423'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionnotification',
            name='field_2_name',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sessionnotification',
            name='field_2_value',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='sessionnotification',
            name='field_3_name',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sessionnotification',
            name='field_3_value',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True),
        ),
    ]
