# Generated by Django 4.1 on 2022-08-21 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0010_alter_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='upload/%Y/%m'),
        ),
    ]
