# Generated by Django 4.1 on 2022-09-02 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0018_alter_voucher_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='cart_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.cartdetail'),
        ),
    ]
