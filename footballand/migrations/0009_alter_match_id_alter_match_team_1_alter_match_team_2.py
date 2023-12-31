# Generated by Django 4.2.4 on 2023-08-09 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('footballand', '0008_alter_match_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='match',
            name='team_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_1', to='footballand.footballteam'),
        ),
        migrations.AlterField(
            model_name='match',
            name='team_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_2', to='footballand.footballteam'),
        ),
    ]
