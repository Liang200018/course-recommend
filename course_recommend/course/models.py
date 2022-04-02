from django.db import models

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone
from DjangoUeditor.models import UEditorField #头部增加这行代码导入UEditorField
# Create your models here.


# 用户
class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    u_id = models.CharField(max_length=20, unique=True, verbose_name="用户id") 
    name = models.CharField(max_length=255, blank=False, unique=True, 
                            verbose_name="用户名")
    password = models.CharField(max_length=20, blank=False, verbose_name="密码")
    created_time = models.DateTimeField('注册时间', default=timezone.now())
    
    class Meta:
        db_table = "user"
    
    def __str__(self):
        return self.name
    
    
# 课程分类
class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="分类")
    index = models.IntegerField(default=999, verbose_name='分类排序')
    
    class Meta:
        db_table = "category"
        verbose_name = '课程分类'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


# 课程标签
class Tag(models.Model):
    name = models.CharField('课程标签', max_length=100)
    
    class Meta:
        verbose_name = '课程标签'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

# 课程
class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    course_id = models.CharField(max_length=50, unique=True, verbose_name="课程id")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                     to_field="category_id",
                                     null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="课程名")
    about = models.TextField('课程介绍', max_length=500, blank=True)
    # 课程详细
    body = UEditorField('内容', width=800, height=500, 
                    toolbars="full", imagePath="upimg/", filePath="upfile/",
                    upload_settings={"imageMaxSize": 1204000},
                    settings={}, command=None, 
                    blank=True, null=True,
                    )
    url = models.URLField("课程地址", blank=True, null=True)
    prerequisites = models.TextField("先修课程", max_length=100, blank=True, null=True)
    
    # 课程封面字段
    img = models.ImageField(verbose_name='课程图片', blank=True, null=True,
                            upload_to='course_img/%Y/%m/%d/')
    user_num = models.PositiveIntegerField("选课人数", default=0, null=True)
    created_time = models.DateTimeField('创建课程时间', default=timezone.now(),
                                        null=True, blank=True)
    
    class Meta:
        db_table = 'course'
        verbose_name = '课程'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

# 学校
class School(models.Model):
    id = models.BigAutoField(primary_key=True)
    sch_id = models.CharField(max_length=50, unique=True, verbose_name="学校id")
    name = models.CharField(max_length=100, verbose_name="学校名")
    about = models.TextField('学校介绍', max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'school'
        verbose_name = '学校'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

# 老师
class Teacher(models.Model):
    id = models.BigAutoField(primary_key=True)
    t_id = models.CharField(max_length=50, unique=True, verbose_name="教师id")
    name = models.CharField(max_length=100, verbose_name="教师名")
    about = models.TextField('教师介绍', max_length=500, blank=True, null=True)
    school = models.ForeignKey('School', to_field='sch_id', 
                               on_delete=models.DO_NOTHING, 
                               verbose_name="任职学校")
    
    class Meta:
        db_table = 'teacher'
        verbose_name = '教师'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name
    
    
# 选课关系
class UserCourse(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('user', to_field='u_id', 
                             on_delete=models.DO_NOTHING,
                             null=True)
    course = models.ForeignKey('course', to_field='course_id', 
                               on_delete=models.DO_NOTHING,
                               null=True)
    created_time = models.DateTimeField("选课日期", default=timezone.now(), null=True)
    modified_time = models.DateTimeField("最近修改日期", auto_now=True, null=True)
    state = models.BooleanField("选课状态", default=True, null=True) # 退课的话，状态变为False
    
    class Meta:
        db_table = 'user_course'
        verbose_name = '选课关系'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return "%s-%s" % (self.user, self.course)

# 推荐表
class Recommend(models.Model):
    recommend_choices = [
        ('hot', 'hot'), #热门推荐
        ('custom', 'customized'), #个性化推荐
        ]
    recommend_cycle_choices = [
        ('h', 'hour'),
        ('d', 'day'),
        ]
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('user', to_field='u_id',
                             on_delete=models.DO_NOTHING)
    course = models.ForeignKey('course', to_field='course_id', 
                               on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField("推荐日期", default=timezone.now())
    
    recommend_type = models.CharField(choices=recommend_choices, max_length=10,
                                      null=True, blank=True)
    recommend_cycle = models.CharField(choices=recommend_choices, max_length=10,
                                       null=True, blank=True)
    
    class Meta:
        db_table = 'recommend'
        verbose_name = '推荐结果'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return "%s-%s-%s" % (self.user, self.course, self.recommend_type)