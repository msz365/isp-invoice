# Generated by Django 3.0.8 on 2020-11-16 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isp_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='service_subscribed',
            field=models.ManyToManyField(blank=True, null=True, to='isp_app.Service'),
        ),
    ]
