# Generated by Django 4.2.4 on 2023-08-07 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('footballand', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='draw_bets',
        ),
    ]
