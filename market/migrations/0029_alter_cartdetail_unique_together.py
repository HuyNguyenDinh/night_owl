# Generated by Django 4.1 on 2022-09-24 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0028_alter_order_voucher_apply'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartdetail',
            unique_together={('customer', 'product_option')},
        ),
    ]
