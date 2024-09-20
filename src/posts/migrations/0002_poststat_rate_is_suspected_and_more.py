# Generated by Django 5.1.1 on 2024-09-20 14:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PostStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('average_rate', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('total_rates', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'post rate stat',
                'verbose_name_plural': 'post rate stats',
            },
        ),
        migrations.AddField(
            model_name='rate',
            name='is_suspected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='rate',
            index=models.Index(fields=['post', 'user'], name='posts_rate_post_id_f0f8b4_idx'),
        ),
        migrations.AddField(
            model_name='poststat',
            name='post',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stat', to='posts.post'),
        ),
    ]