# Generated by Django 3.0 on 2024-12-05 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(null=True)),
                ('Reason', models.CharField(max_length=150, null=True)),
                ('Amount', models.CharField(max_length=150, null=True)),
                ('staffname', models.CharField(max_length=150, null=True)),
            ],
        ),
    ]