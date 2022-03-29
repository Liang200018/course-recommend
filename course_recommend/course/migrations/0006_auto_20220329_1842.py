# Generated by Django 3.0.8 on 2022-03-29 10:42

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_auto_20220329_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourse',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 29, 10, 42, 57, 628966, tzinfo=utc), verbose_name='选课日期'),
        ),
        migrations.CreateModel(
            name='Recommend',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=datetime.datetime(2022, 3, 29, 10, 42, 57, 628966, tzinfo=utc), verbose_name='推荐日期')),
                ('recommend_type', models.CharField(blank=True, choices=[('hot', 'hot'), ('custom', 'customized')], max_length=10, null=True)),
                ('recommend_cycle', models.CharField(blank=True, choices=[('hot', 'hot'), ('custom', 'customized')], max_length=10, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='course.Course', to_field='course_id')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='course.User')),
            ],
        ),
    ]
