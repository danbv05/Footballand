# Generated by Django 4.2.4 on 2023-08-15 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('footballand', '0014_player_previous_login_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='previous_login_date',
            new_name='previous_login',
        ),
    ]
