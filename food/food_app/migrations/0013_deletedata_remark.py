# Generated by Django 3.0 on 2024-12-10 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_app', '0012_deletedata_item_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='deletedata',
            name='remark',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
