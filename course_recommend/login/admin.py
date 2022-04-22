from django.contrib import admin

# Register your models here.
from course.models import User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 文章列表里显示想要显示的字段
    list_display = ('u_id', 'name', 'password', 'created_time')
    # 满50条数据就自动分页
    list_per_page = 50
    # 后台数据列表排序方式   
    ordering = ('name',)
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('password', )
   