# Generated by Django 4.2.14 on 2025-02-24 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_alter_ticket_closed_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subproject',
            name='sub_project_id',
        ),
    ]
