# Generated by Django 4.1 on 2022-10-17 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0045_alter_user_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='cart_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.cartdetail'),
        ),
    ]
