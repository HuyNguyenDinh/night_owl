# Generated by Django 4.1 on 2022-10-05 03:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0039_room_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
