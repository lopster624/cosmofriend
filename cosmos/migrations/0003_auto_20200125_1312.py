# Generated by Django 3.0.2 on 2020-01-25 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cosmos', '0002_auto_20200125_0134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friends',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photos/%Y/%m/%d'),
        ),
    ]
