# Generated by Django 4.1 on 2022-09-01 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0014_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'UnCheckout'), (1, 'Approving'), (2, 'Pending'), (3, 'Completed'), (4, 'Canceled')], default=0),
        ),
    ]
