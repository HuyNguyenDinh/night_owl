# Generated by Django 4.1 on 2022-10-06 01:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0040_message_created_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='provider',
        ),
    ]
