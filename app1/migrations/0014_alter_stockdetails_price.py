# Generated by Django 4.0.2 on 2022-03-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0013_remove_stockdetails_email_alter_adminregi_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdetails',
            name='price',
            field=models.FloatField(),
        ),
    ]
