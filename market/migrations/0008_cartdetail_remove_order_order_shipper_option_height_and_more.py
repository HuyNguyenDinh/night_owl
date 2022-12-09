# Generated by Django 4.1 on 2022-08-18 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_remove_product_warehouse'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_shipper',
        ),
        migrations.AddField(
            model_name='option',
            name='height',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='option',
            name='length',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='option',
            name='weight',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='option',
            name='width',
            field=models.PositiveBigIntegerField(default=1),
        ),
        migrations.DeleteModel(
            name='Shipper',
        ),
        migrations.AddField(
            model_name='cartdetail',
            name='product_option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.option'),
        ),
    ]