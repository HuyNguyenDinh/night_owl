# Generated by Django 4.1 on 2022-09-28 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0031_alter_cartdetail_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='payed_for_seller',
            field=models.BooleanField(default=False),
        ),
    ]
