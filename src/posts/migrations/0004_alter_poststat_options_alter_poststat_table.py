# Generated by Django 5.1.1 on 2024-09-20 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_rename_average_rate_poststat_average_rates'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poststat',
            options={'verbose_name': 'Post Stat', 'verbose_name_plural': 'Post Stats'},
        ),
        migrations.AlterModelTable(
            name='poststat',
            table='post_stat',
        ),
    ]