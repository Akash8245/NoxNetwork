# Generated by Django 5.0.6 on 2024-06-19 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_user_commission_remove_user_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.user'),
        ),
    ]