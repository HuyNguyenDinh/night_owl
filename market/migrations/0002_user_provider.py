# Generated by Django 4.1 on 2022-08-15 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='provider',
            field=models.IntegerField(choices=[(0, 'default'), (1, 'facebook'), (2, 'google')], default=0),
        ),
    ]
