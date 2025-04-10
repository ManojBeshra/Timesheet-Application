# Generated by Django 4.2.18 on 2025-01-29 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_remove_customer_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='customer_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer_status'),
        ),
    ]
