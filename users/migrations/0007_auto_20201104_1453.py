# Generated by Django 3.1.2 on 2020-11-04 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20201030_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('TR', 'Trialing'), ('AC', 'Active'), ('IN', 'Incomplete'), ('IP', 'Incomplete Expired'), ('PD', 'Past Due'), ('CA', 'Canceled'), ('UN', 'Unpaid')], default='TR', max_length=120),
        ),
    ]
