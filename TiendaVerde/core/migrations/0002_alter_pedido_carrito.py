# Generated by Django 5.1.2 on 2024-10-20 23:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='carrito',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.carrito'),
        ),
    ]
