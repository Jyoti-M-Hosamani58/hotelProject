# Generated by Django 3.0 on 2024-12-10 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_app', '0005_auto_20241210_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
