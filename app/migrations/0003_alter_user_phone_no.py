# Generated by Django 5.0.6 on 2024-06-05 15:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_referedby_user_referred_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(max_length=14, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+91 XXXXXXXXXX '.", regex='^\\+91 \\d{10}$')]),
        ),
    ]
