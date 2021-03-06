# Generated by Django 3.1.2 on 2020-10-30 21:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20201027_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='active',
        ),
        migrations.AddField(
            model_name='subscription',
            name='cancel_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 30, 21, 30, 8, 515338, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='cancel_at_period_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('TR', 'Trialing'), ('AC', 'Active'), ('IN', 'Incomplete'), ('IP', 'Incomplete Expired'), ('PD', 'Past Due'), ('CA', 'Canceled'), ('UN', 'Unpaid')], default='AC', max_length=120),
        ),
    ]
