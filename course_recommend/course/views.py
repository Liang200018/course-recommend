'''
前后端结合的地方，涉及到数据库和HTMl
读取数据库中的对象，结合模板渲染
'''
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import (User, UserCourse, Course, Category, 
                     Tag, School, Teacher, Recommend)

from course.recommend import ItemCF

class PageResource:
    
    def __init__(self, page_name):
        self.page_name = page_name
        self.resource_list = {}
        
    def get_resource(self, name):
        '''返回资源'''
        if self.resource_list.get('name') is None:
            raise AttributeError("%s not exists" % (name))
        return self.resource_list['name']
    
    def set_resource(self, name, func, *args, **kwargs):
        '''设置资源'''
        resource = func(*args, **kwargs) # 获取资源
        self.resource_list[name] = resource        

    def __str__(self):
        return "%s PageResource" % self.page_name
        
class PageResourceManager:
    "管理多个页面的资源"
    def __init__(self):
        self.page_list = {}
    
    def get_page_resouce(self, page_name):
        if self.page_list.get(page_name) is None:
            raise AttributeError("%s page_resouce not exists" % (page_name))
        return self.page_list[page_name]      
    
    def set_page_resource(self, page_name, page_resource):
        if not isinstance(page_resource, PageResource):
            raise TypeError("%s is not a PageResource object" % page_resource)
        self.page_list[page_name] = page_resource


page_manager = PageResourceManager()

def view_with_resource(page_name):
    '''带页面资源名称的装饰器'''
    def resource_decorator(func):
        def wrapper(*args, **kwargs): # 装饰器获取被修饰函数的参数
            # print(page_name)
            # print(func)
            # print(args)
            # print(kwargs)
            pg_resource = page_manager.get_page_resouce(page_name=page_name)
            resource_list = pg_resource.resource_list # 传递给resource_list
            
            request = args[0]
            return func(request, resource_list=resource_list) # 视图函数执行
            
        wrapper.__name__ = func.__name__ # 不改变被修饰函数的名字
        return wrapper
    return resource_decorator   


# 首页
'''
    allcategory = resource_list['allcategory'] # Category.objects.all() #通过Category表查出所有分类
    
    # 展示轮播图
    allbanner # Banner.objects.filter(is_active=True)[0:4] # 首页幻灯片
    recommend #Recommend.objects.get(id=1)
    
    # 获得首页课程推荐
    allrecommend 
    #Article.objects.filter(recommend=recommend)[0:3] #查询推荐位ID为1的文章
    
    # 获得最新课程推荐
    latest_recommend  
    #Article.objects.all().order_by('-id')[0:10] # 最新文章
    
    # 获得课程热门排行
    hot = resource_list['hot'] 
    #Article.objects.all().order_by('views')[:10] # 热门排序, 通过浏览数进行排序
    
    # 获得热门课程推荐列表
    # 排序规则
    # 这里是简单化通过切片选择
    hot_recommend 
    # Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] # 热门推荐
    
    tags
'''


# 得到index页面资源的方法
def get_allcategory():
    res = Category.objects.all().order_by('-index')
    return res

def get_allbanner():
    '''return None 或者 资源'''
    return None

def get_allrecommend():
    
    return None

def get_latest_recommend():
    return None

def get_hot():
    return None

def get_hot_recommend():
    return None

def get_tags():
    return None


r_index = PageResource('index')
page_manager.set_page_resource('index', r_index) # 添加index页面资源
r_index.set_resource('allcategory', func=get_allcategory)
r_index.set_resource('allbanner', func=get_allbanner)
r_index.set_resource('allrecommend', func=get_allrecommend)
r_index.set_resource('latest_recommend', func=get_latest_recommend)
r_index.set_resource('hot', func=get_hot)
r_index.set_resource('hot_recommend', func=get_hot_recommend)
r_index.set_resource('tags', func=get_tags)


@view_with_resource('index') # 这里的page_name 要和page_manager.set_page_resource(page_name)一致
def ViewIndex(request, **kwargs):
    
    # model retrieve
    # 获得课程首页分类
    resource_list = kwargs['resource_list'] if kwargs.get('resource_list') else None
    
    resource_context = {'allcategory': [],
                'allbanner': [],
                'allrecommend': [],
                'latest_recommend': [],
                'hot': [],
                'hot_recommend': [],
                'tags': [],
                }
    # 如果没有添加资源就为空列表
    for key, value in resource_list.items():
        if key in resource_context.keys() and value: 
            resource_context[key] = value 

    return render(request, template_name='index.html', context=resource_context)
    # return HttpResponse("hello")
    

# # 列表页
# def ViewList(request, lid):
#     category_article = Article.objects.filter(category=Category.objects.get(id=lid))#获取通过URL传进来的lid，然后筛选出对应文章
    
#     category = Category.objects.get(id=lid) #获取当前文章的栏目名
#     hot = Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] #右侧的热门推荐
#     allcategory = Category.objects.all() #导航所有分类
#     tags = Tag.objects.all() #右侧所有文章标签

#     return render(request, 'list.html', locals())

# # 内容页
# def ViewShow(request, sid):
#     show = Article.objects.get(id=sid) #查询指定ID的文章
#     allcategory = Category.objects.all() #导航上的分类
#     tags = Tag.objects.all() #右侧所有标签
#     hot_recommend = Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] # 热门推荐
    
#     hot = Article.objects.all().order_by('-views')[:10]#内容下面的您可能感兴趣的文章，随机推荐
    
#     previous_blog = Article.objects.filter(created_time__gt=show.created_time, 
#                                            category=show.category.id).first()
#     next_blog = Article.objects.filter(created_time__lt=show.created_time, 
#                                        category=show.category.id).last()
    
#     # 更新浏览量
#     show.views = show.views + 1
#     show.save()
#     return render(request, 'show.html', locals())

# def ViewPage(request):
#     pass

# # 标签页
# def ViewTag(request, tag):
#     tag_article = Article.objects.filter(tags__name=tag) #通过文章标签进行查询文章
#     hot = Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] #右侧的热门推荐
#     allcategory = Category.objects.all()    
#     tname = Tag.objects.get(name=tag) #获取当前搜索的标签名
    
#     page = request.GET.get('page')
#     tags = Tag.objects.all()
    
    
#     paginator = Paginator(tag_article, 5)
#     try:
#         list = paginator.page(page)  # 获取当前页码的记录
#     except PageNotAnInteger:
#         list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
#     except EmptyPage:
#         list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
#     return render(request, 'tags.html', locals())

# # 搜索页
# def ViewSearch(request):
    
#     ss=request.GET.get('search')#获取搜索的关键词
#     search_article = Article.objects.filter(title__icontains=ss)#获取到搜索关键词通过标题进行匹配
    
#     hot = Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] #右侧的热门推荐
#     allcategory = Category.objects.all()
    
#     page = request.GET.get('page')
#     tags = Tag.objects.all()
#     paginator = Paginator(search_article, 10)
#     try:
#         list = paginator.page(page) # 获取当前页码的记录
#     except PageNotAnInteger:
#         list = paginator.page(1) # 如果用户输入的页码不是整数时,显示第1页的内容
#     except EmptyPage:
#         list = paginator.page(paginator.num_pages) # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
#     return render(request, 'search.html', locals())

# # 关于页
# def ViewAbout(request):
#     allcategory = Category.objects.all()
#     return render(request, 'page.html',locals())

