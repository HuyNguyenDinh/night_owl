# Generated by Django 4.1 on 2022-08-21 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0009_remove_product_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
