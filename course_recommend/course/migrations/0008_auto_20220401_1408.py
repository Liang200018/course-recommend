# Generated by Django 3.0.8 on 2022-04-01 06:08

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_auto_20220401_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommend',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 6, 8, 3, 163301, tzinfo=utc), verbose_name='推荐日期'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 6, 8, 3, 161300, tzinfo=utc), verbose_name='注册时间'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='course.Course', to_field='course_id'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 1, 6, 8, 3, 162297, tzinfo=utc), null=True, verbose_name='选课日期'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='modified_time',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='最近修改日期'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='state',
            field=models.BooleanField(default=True, null=True, verbose_name='选课状态'),
        ),
        migrations.AlterField(
            model_name='usercourse',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='course.User'),
        ),
    ]
