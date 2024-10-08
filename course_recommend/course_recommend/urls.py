"""course_recommend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from django.conf.urls.static import static

#导入静态文件模块
from django.conf import settings
#导入配置文件里的文件上传配置

from course import views
import login.views as login_view
 
from test_app.views import get_name
urlpatterns = [
    # 登录页
    
    path('index/', views.ViewIndex),
    path('login/', login_view.login),
    path('register/', login_view.register),
    path('logout/', login_view.logout),
    
    path('',  views.ViewIndex, name='index'),#网站首页
    path('mycourse/', views.ViewMyCourse, name='mycourse'), # 查看自己的课程

    path('list-<int:lid>.html', views.ViewList, name='list'),#列表页
    path('show-<int:sid>.html', views.ViewShow, name='show'),#内容页
    path('like/', views.ReceiveLikeCourse, name='like_course'), # 接受用户喜欢课程的数据
    # path('tag/<tag>', views.ViewTag, name='tags'),#标签列表页
    path('search/', views.ViewSearch, name='search'),#搜索列表页
    path('about/', views.ViewAbout, name='about'),#联系我们单页
    
    path('admin/', admin.site.urls),
    
    re_path('^stiaic/(?P<path>.*)', serve,{'document_root': settings.STATIC_ROOT}), # 用于处理static里的文件

    re_path('^media/(?P<path>.*)', serve,{'document_root': settings.MEDIA_ROOT}), # 用于处理上传的文件
    
    # path('course/', include('course.urls')), # 路由转发
    # path('ueditor/', include('DjangoUeditor.urls')), # 富文本编辑器
    # re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),#增加此行
    
    # path('test_app/', include('test_app.urls')),
    # path('your-name/', get_name),
    
]
