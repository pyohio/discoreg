# Generated by Django 3.0.8 on 2020-07-24 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SessionNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('url', models.URLField(blank=True, default=None, null=True)),
                ('description', models.CharField(blank=True, default='', max_length=2048, null=True)),
                ('color_hex_string', models.CharField(default='ffffff', max_length=6)),
                ('field_1_name', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('field_1_value', models.CharField(blank=True, default=None, max_length=1024, null=True)),
                ('author_name', models.CharField(blank=True, default='Next up:', max_length=256, null=True)),
                ('send_by', models.DateTimeField()),
                ('sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
