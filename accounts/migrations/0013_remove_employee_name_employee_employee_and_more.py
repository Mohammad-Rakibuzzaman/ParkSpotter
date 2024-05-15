# Generated by Django 5.0 on 2024-05-15 09:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_zone_remove_booking_park_detail_booking_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='name',
        ),
        migrations.AddField(
            model_name='employee',
            name='employee',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='employee',
            name='park_owner_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees_owner', to='accounts.parkowner'),
        ),
    ]
