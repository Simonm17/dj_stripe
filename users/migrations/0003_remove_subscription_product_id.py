# Generated by Django 3.1.2 on 2020-10-26 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201025_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='product_id',
        ),
    ]
