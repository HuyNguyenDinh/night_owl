# Generated by Django 4.1 on 2022-08-11 09:42

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=255)),
                ('unit_in_stock', models.BigIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('completed_date', models.DateField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.IntegerField(choices=[(0, 'Customer'), (1, 'Store'), (2, 'Admin')], default=0),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('sold_amount', models.BigIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
                ('categories', models.ManyToManyField(to='market.category')),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='night_owl/product')),
                ('product_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.option')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('status', models.IntegerField(choices=[(0, 'Approving'), (1, 'Pending'), (2, 'Completed'), (3, 'Canceled')], default=0)),
                ('shipping_id', models.CharField(max_length=255)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.order')),
            ],
        ),
        migrations.AddField(
            model_name='option',
            name='base_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.product'),
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('payed', models.BooleanField(default=False)),
                ('order_detail', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.orderdetail')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(default='Viet Nam', max_length=100)),
                ('province_id', models.IntegerField()),
                ('district_id', models.IntegerField()),
                ('ward_id', models.IntegerField()),
                ('street', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
