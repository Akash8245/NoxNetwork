# Generated by Django 4.1.13 on 2024-09-01 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_rename_no_people_refered_user_no_people_referred'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='no_people_referred',
            new_name='no_people_refered',
        ),
    ]
