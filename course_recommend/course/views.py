'''
前后端结合的地方，涉及到数据库和HTMl
读取数据库中的对象，结合模板渲染
'''
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import *

# 首页
def ViewIndex(request):
    
    # # model retrieve
    # allcategory = Category.objects.all() #通过Category表查出所有分类
    # allbanner = Banner.objects.filter(is_active=True)[0:4] # 首页幻灯片
    
    # recommend = Recommend.objects.get(id=1)
    # allrecommend = Article.objects.filter(recommend=recommend)[0:3] #查询推荐位ID为1的文章
    # latest_article = Article.objects.all().order_by('-id')[0:10] # 最新文章
    # hot = Article.objects.all().order_by('views')[:10] # 热门排序, 通过浏览数进行排序
    
    # # 排序规则
    # # 这里是简单化通过切片选择
    # hot_recommend = Article.objects.filter(recommend=Recommend.objects.get(id=3))[:6] # 热门推荐
    
    # tags = Tag.objects.all()
    
    # # context
    # context = {'allcategory': allcategory,
    #            'allbanner': allbanner,
    #            'allrecommend': allrecommend,
    #            'latest_article': latest_article,
    #            'hot': hot,
    #            'hot_recommend': hot_recommend,
    #            'tags': tags,
    #            }
    

    # return render(request, template_name='index.html', context=context)
    return HttpResponse("hello")
    

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

