# Generated by Django 3.0.8 on 2022-02-21 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20220221_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
