# Generated by Django 3.0.8 on 2022-04-01 04:17

import DjangoUeditor.models
import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20220330_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='body',
            field=DjangoUeditor.models.UEditorField(blank=True, null=True, verbose_name='内容'),
        ),
        migrations.AlterField(
            model_name='course',
            name='user_num',
            field=models.PositiveIntegerField(default=0, null=True, verbose_name='选课人数'),
        ),
        migrations.AlterField(
            model_name='recommend',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 4, 17, 45, 404178, tzinfo=utc), verbose_name='推荐日期'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 4, 17, 45, 402183, tzinfo=utc), verbose_name='注册时间'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 4, 17, 45, 404178, tzinfo=utc), verbose_name='选课日期'),
        ),
    ]
