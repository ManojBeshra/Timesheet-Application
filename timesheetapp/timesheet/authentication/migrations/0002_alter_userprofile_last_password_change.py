# Generated by Django 4.2.20 on 2025-07-04 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='last_password_change',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
