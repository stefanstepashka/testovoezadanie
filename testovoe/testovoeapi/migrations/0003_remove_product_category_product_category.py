# Generated by Django 4.2 on 2023-04-04 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testovoeapi', '0002_remove_category_parent_category_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(to='testovoeapi.category'),
        ),
    ]
