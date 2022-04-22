from django.contrib import admin

from .models import Category, Course 
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'index')
    # 文章列表里显示想要显示的字段
    list_per_page = 50
    # 满50条数据就自动分页
    ordering = ('-index',)
    #后台数据列表排序方式
    list_display_links = ('name', 'index')
    # 设置哪些字段可以点击进入编辑界面
    
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'url', 'user_num')
    
    list_per_page = 50
    
    ordering = ('id',)
    
    list_display_links = ('course_id', 'name', 'url')
    
