# Generated by Django 3.0.8 on 2022-03-29 10:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_auto_20220329_1842'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recommend',
            options={'verbose_name': '推荐结果', 'verbose_name_plural': '推荐结果'},
        ),
        migrations.AlterField(
            model_name='recommend',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 29, 10, 46, 27, 546441, tzinfo=utc), verbose_name='推荐日期'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 29, 10, 46, 27, 546441, tzinfo=utc), verbose_name='选课日期'),
        ),
        migrations.AlterModelTable(
            name='recommend',
            table='recommend',
        ),
    ]
