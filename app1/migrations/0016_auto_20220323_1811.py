# Generated by Django 2.1.5 on 2022-03-23 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0015_auto_20220323_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdetails',
            name='productName',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
