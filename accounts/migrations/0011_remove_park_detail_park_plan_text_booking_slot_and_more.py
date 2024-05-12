# Generated by Django 4.2.13 on 2024-05-12 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_employee_vehicle_alter_park_detail_capacity_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='park_detail',
            name='park_plan_text',
        ),
        migrations.AddField(
            model_name='booking',
            name='slot',
            field=models.IntegerField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], default=1),
        ),
        migrations.AlterField(
            model_name='park_detail',
            name='capacity',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
