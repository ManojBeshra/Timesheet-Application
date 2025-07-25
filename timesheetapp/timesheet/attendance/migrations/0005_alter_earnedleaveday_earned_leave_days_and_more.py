# Generated by Django 4.2.23 on 2025-07-13 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0004_earnedleaveday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earnedleaveday',
            name='earned_leave_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='earnedleaveday',
            name='joined_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='earnedleaveday',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
