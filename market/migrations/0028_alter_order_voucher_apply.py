# Generated by Django 4.1 on 2022-09-22 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0027_rename_shipping_order_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='voucher_apply',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.voucher'),
        ),
    ]
