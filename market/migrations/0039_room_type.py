# Generated by Django 4.1 on 2022-10-04 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0038_room_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='type',
            field=models.IntegerField(choices=[(0, 'single'), (1, 'group')], default=0),
        ),
    ]
