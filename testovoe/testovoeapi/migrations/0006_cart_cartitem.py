# Generated by Django 4.2 on 2023-04-05 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testovoeapi', '0005_product_subcategory_alter_subcategory_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testovoeapi.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testovoeapi.product')),
            ],
        ),
    ]
