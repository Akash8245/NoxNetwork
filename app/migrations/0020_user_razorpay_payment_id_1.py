# Generated by Django 4.1.13 on 2024-07-01 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_course_remove_user_commission_percent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='razorpay_payment_id_1',
            field=models.CharField(default='', max_length=255),
        ),
    ]