# Generated by Django 5.0.6 on 2024-06-19 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_user_referred_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referred_by',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]