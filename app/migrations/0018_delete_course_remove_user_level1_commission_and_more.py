# Generated by Django 5.0.6 on 2024-06-20 10:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_user_level1_commission_user_level1_referrer_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Course',
        ),
        migrations.RemoveField(
            model_name='user',
            name='level1_commission',
        ),
        migrations.RemoveField(
            model_name='user',
            name='level1_referrer',
        ),
        migrations.RemoveField(
            model_name='user',
            name='level2_commission',
        ),
        migrations.RemoveField(
            model_name='user',
            name='level2_referrer',
        ),
        migrations.AddField(
            model_name='user',
            name='commission_percent',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='user',
            name='level',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='user',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.user'),
        ),
    ]
