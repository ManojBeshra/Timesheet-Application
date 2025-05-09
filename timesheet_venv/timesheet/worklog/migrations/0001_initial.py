# Generated by Django 4.2.16 on 2025-02-28 14:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task', '0007_rename_project_id_subproject_project'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='worklog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('workdone', models.CharField(blank=True, max_length=200, null=True)),
                ('hours', models.IntegerField(blank=True, null=True)),
                ('billable', models.BooleanField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=200, null=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('week', models.CharField(blank=True, max_length=100)),
                ('priority', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='task.priority_type')),
                ('project_support', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worklog_project_support', to='task.ticket_type')),
                ('ticket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worklog_ticket', to='task.ticket')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
