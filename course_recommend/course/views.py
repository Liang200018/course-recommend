'''
前后端结合的地方，涉及到数据库和HTMl
读取数据库中的对象，结合模板渲染
'''
import threading
import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import (User, UserCourse, Course, Category, 
                     Tag, School, Teacher, Recommend)

from course.recommend import ItemCF, LFMRecommend
from course.measure import ItemCFModel, LFModel



class PageResource:
    """每一个视图函数被触发，都会新建实例
    """
    def __init__(self, page_name):
        self.page_name = page_name
        self.resource_list = {}
        self.request = None # 动态赋值
        self.thread_list = []
    
    def notify(self):
        """
        线程阻塞,资源完成后，返回True

        Returns
        -------
        True or False.
        """
        
        # for t in self.thread_list:
        #     t.start()
        #     print("线程加载资源就绪")
        
        for t in self.thread_list:
            t.join()
        print("%s个线程" % len(self.thread_list)) # 注意线程start后才存在
        print("所有加载资源的线程结束")
        
        # 线程不同start两次
        # 完成资源的加载后，清理线程，和request
        self.thread_list.clear()
        self.request = None
        return True            
            
    def get_resource(self, name):
        '''返回资源'''
        if self.resource_list.get('name') is None:
            raise AttributeError("%s not exists" % (name))
        return self.resource_list['name']
    
    def thread_set_resource(self, name, func, *args, **kwargs):
        """
        传递给一般的set_resource，以一种阻塞的方式设置资源
        name: str
        func: function object
        args: 传入获取资源的位置参数
        kwargs: 传入获取资源的关键字参数
        Returns
        -------
        None.
        """
        combined_args = (name, func) + args
        # print(combined_args)
        t = threading.Thread(target=self.set_resource, args=combined_args, kwargs=kwargs)
        
        # print("创建新的线程加载资源")
        while 1:
            if len(self.thread_list) <= 10:
                self.thread_list.append(t) # 加入线程列表
                t.start()
                break
            else:
                time.sleep(1)
                break
        # print(len(self.thread_list))
    
    
    def set_resource(self, name, func, *args, **kwargs):
        """
        设置资源        

        Parameters
        ----------
        name : str 资源名
        func : function object 获取资源的函数.
        *args : 获取资源函数的位置参数.
        **kwargs : 获取资源函数的关键字参数.
        
        thread_set_resouce(name, func, ......) 传入的参数最终会给到get_XXX
        get_XXX(request, *args, **kwargs)

        Returns
        -------
        None.

        """

        while 1:
            if self.request: # 准备加载
                resource = func(request=self.request, *args, **kwargs) # 获取资源
                self.resource_list[name] = resource
                print("页面资源加载完毕")
                break
            else:
                # 阻塞还是异步？
                # 延迟加载，开一个线程，完成后
                print("继续等待时机加载资源")
        

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

itemcf_model = ItemCFModel(ItemCF(5)) 
train = itemcf_model.model.user_items # 生产模式下，用全部数据
itemcf_model.fit(train=train) # 必须要训练后，才可以recommend


def view_with_resource(page_name):
    '''带页面资源名称的装饰器
    先于PageResource获取资源
    '''
    def resource_decorator(func):
        """
        
        视图函数的装饰器

        Parameters
        ----------
        func : view function.

        Returns: wrapper
        
        """
        def wrapper(*args, **kwargs): 
            """

            Parameters
            ----------
            *args : tumple
                获取被修饰函数的位置参数
            **kwargs : dict
                获取被修饰函数的关键字参数.

            视图函数需要*args, **kwargs
            Returns
            -------
            HttpResponse
                视图函数的返回结果.

            """
    
            # print(page_name)
            # print(func)
            # print(args)
            # print(kwargs)
            pg_resource = page_manager.get_page_resouce(page_name=page_name) # 获得视图函数中的页面资源管理器
            request = args[0]
            pg_resource.request = request   # 一些动态资源需要结合request获取
            

            # # 注意pg_resource不可以在request赋值前加载
            # resource_list = pg_resource.resource_list # 传递给resource_list
            # print("一共有 %d 种页面资源" % len(resource_list))
            
            # 线程不同start两次
            # pg_resource.thread_list = []
            # pg_resource.request = None
            return func(pg_resource.request, resource_list=pg_resource.resource_list, 
                        *args[1:], **kwargs) # 视图函数执行
            
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

    # 获得最新课程推荐
    latest_recommend  
    
    # 获得课程热门排行
    hot = resource_list['hot'] 
    
    # 获得热门课程推荐列表
    hot_recommend 

    tags
'''


# 得到index页面资源的方法, 静态资源，动态资源
def get_allcategory(request):
    res = Category.objects.all().order_by('-index')
    print("执行结束")
    return res

def get_allbanner(request):
    '''return None 或者 资源'''
    print("执行结束")
    return None

def get_allrecommend(request, **kwargs):
    """不同地方的推荐，给的推荐列表大小不一样
    kwargs :
        option N 推荐列表的大小
    """
    
    # 用户身份
    N = kwargs['N'] if kwargs.get('N') else 3
    res = {}
    if request and request.session.get('is_login'):
        user_id =  request.session.get('user_id')
        
        course_id_list = itemcf_model.recommend(user=user_id,  N=N)
        
        # To-do LFM模型读取两个矩阵，获取推荐列表
        # 直接读取LFM的结果，LFM模型把推荐结果写到推荐表中，供读取
        
        print(course_id_list)
        if len(course_id_list) > 0:
            res = []
            # 按照course_id_list 调整顺序
            for course_id in course_id_list:
                course = Course.objects.get(course_id=course_id)
                res.append(course)
            
            # To-do 重排环节, 根据课程内容提取特征，将与已选择课程内容相近的课程排名提高。
            
            return res
        else:
            res = Course.objects.all().order_by('?')[:N] # 用户没有选择课程
        print(user_id)
        
    else:
        # request.session.get('is_login')): # 游客身份
        res = Course.objects.all().order_by('?')[:N]
        # print(res)
    
    # print("get all recommend")
    print("执行结束")
    return res

def get_latest_recommend(request):
    res = Course.objects.all().order_by('-id')[0:100]
    print("执行结束")
    print("最新课程 %s" % len(res))
    return res 

def get_hot(request):
    res = Course.objects.all().order_by('-user_num')[0:10]
    print("执行结束")
    return res

def get_hot_recommend(request):
    # 用户身份
    res = {}
    if request and request.session.get('is_login'):
        user_id =  request.session.get('user_id')
        course_id_list = itemcf_model.recommend(user=user_id,  N=20) # 推荐20个
        # print(course_id_list)
        if len(course_id_list) > 0:
            res = Course.objects.filter(course_id__in=course_id_list).order_by('-user_num')[:10]
        else:
            res = Course.objects.all().order_by('-user_num')[:10] # 用户没有选择课程
        # print(user_id)
    else:
        # request.session.get('is_login')): # 游客身份
        res = Course.objects.all().order_by('-user_num')[:10]
        print(res)
    print("执行结束")
    return res

def get_tags(request):
    res = Tag.objects.all()
    print("执行结束")
    return res


r_index = PageResource('index')
page_manager.set_page_resource('index', r_index) # 添加index页面资源

@view_with_resource('index') # 这里的page_name 要和page_manager.set_page_resource(page_name)一致
def ViewIndex(request, **kwargs):
    
    
    r_index.thread_set_resource('allcategory', func=get_allcategory)
    r_index.thread_set_resource('allbanner', func=get_allbanner)
    r_index.thread_set_resource('allrecommend', func=get_allrecommend)
    r_index.thread_set_resource('latest_recommend', func=get_latest_recommend)
    r_index.thread_set_resource('hot', func=get_hot)
    r_index.thread_set_resource('hot_recommend', func=get_hot_recommend)
    r_index.thread_set_resource('tags', func=get_tags)
    
    # 通知，进程加载资源完成
    r_index.notify()
    
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

    

# -------------
r_list = PageResource('list')
page_manager.set_page_resource('list', r_list) # 添加index页面资源

def get_category_course(request, *args, **kwargs):
    '''得到分类下的课程'''
    res = []
    lid = int(kwargs['lid']) if kwargs.get('lid') else None
    try:
        category = Category.objects.get(category_id=lid)
    except (Category.DoesNotExist, Category.MultipleObjectsReturned) as e:
        print(e.args)
    except Exception as e:
        print(e.args)
    else:
        #获取通过URL传进来的lid，然后筛选出对应文章
        res = Course.objects.filter(category_id=category.category_id)
    print("执行结束")
    return res
    
def get_category(request, *args, **kwargs):
    '''得到分类'''
    res = []
    lid = kwargs['lid'] if kwargs.get('lid') else None
    try:
        res = Category.objects.get(category_id=lid)
    except (Category.DoesNotExist, Category.MultipleObjectsReturned) as e:
        print(e.args)
    except Exception as e:
        print(e.args)
    
    print("执行结束")
    return res

# 列表页
@view_with_resource('list')
def ViewList(request, lid=None, **kwargs):
    r_list.thread_set_resource('allcategory', func=get_allcategory)
    r_list.thread_set_resource('allrecommend', func=get_allrecommend)
    r_list.thread_set_resource('hot_recommend', func=get_hot_recommend)
    r_list.thread_set_resource('tags', func=get_tags)
    
    # 页面独有资源
    r_list.thread_set_resource('category_course', func=get_category_course, lid=lid)
    r_list.thread_set_resource('category', func=get_category, lid=lid)
    # 通知，进程加载资源完成
    r_list.notify()
    resource_list = kwargs['resource_list'] if kwargs.get('resource_list') else None
    
    resource_context = {'allcategory': [],
                'allbanner': [],
                'allrecommend': [],
                'hot': [],
                'hot_recommend': [],
                'tags': [],
                'category': None,
                'category_course': None,
                }
    # 如果没有添加资源就为空列表
    for key, value in resource_list.items():
        if key in resource_context.keys() and value: 
            resource_context[key] = value 
    
    return render(request, 'list.html', context=resource_context)


# -------------
r_show = PageResource('show')
page_manager.set_page_resource('show', r_show) # 添加index页面资源

def get_show_course(request, *args, **kwargs):
    '''得到课程'''
    res = []
    sid = int(kwargs['sid']) if kwargs.get('sid') else None
    print("sid: ", sid)
    try:
        show = Course.objects.get(id=sid)
    except (Category.DoesNotExist, Category.MultipleObjectsReturned) as e:
        print(e.args)
    except Exception as e:
        print(e.args)
    else:
        #获取通过URL传进来的lid，然后筛选出对应文章
        res = show
    print("执行结束")
    return res

def get_previous_course(request, **kwargs):
    '''得到当前分类下课程的前一个课程'''
    res = []
    sid = int(kwargs['sid']) if kwargs.get('sid') else None
    
    try:
        show = Course.objects.get(id=sid)
        res = Course.objects.filter(created_time__gt=show.created_time, 
                                            category_id=show.category_id).first()
    except (Category.DoesNotExist, Category.MultipleObjectsReturned) as e:
        print(e.args)
    except Exception as e:
        print(e.args)
    else:
        res = show
    print("执行结束")
    return res    

def get_next_course(request, **kwargs):
    res = []
    sid = int(kwargs['sid']) if kwargs.get('sid') else None
    
    try:
        show = Course.objects.get(id=sid)
        res = Course.objects.filter(created_time__lt=show.created_time, 
                                        category_id=show.category_id).last()
    except (Category.DoesNotExist, Category.MultipleObjectsReturned) as e:
        print(e.args)
    except Exception as e:
        print(e.args)
    else:
        res = show
    print("执行结束")
    return res    


# 内容页
@view_with_resource('show')
def ViewShow(request, sid=None, **kwargs):
    """
    Parameters
    ----------
    request : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        -sid 课程id.
    """
    r_show.thread_set_resource('allcategory', func=get_allcategory)
    
    r_show.thread_set_resource('hot_recommend', func=get_hot_recommend)
    r_show.thread_set_resource('tags', func=get_tags)
    
    r_show.thread_set_resource('allrecommend', func=get_allrecommend, N=20) #内容下面的您可能感兴趣的文章，随机推荐
    
    # 页面独有资源
    r_show.thread_set_resource('show', func=get_show_course, sid=sid)
    r_show.thread_set_resource('previous_course', func=get_previous_course, sid=sid)
    r_show.thread_set_resource('next_course', func=get_next_course, sid=sid)
    
    # 通知，进程加载资源完成
    r_show.notify()
    resource_list = kwargs['resource_list'] if kwargs.get('resource_list') else None
    
    resource_context = {'allcategory': [],
                'allrecommend': [],
                'show': [],
                'hot_recommend': [],
                'tags': [],
                'previous_course': None,
                'next_course': None,
                }
    # 如果没有添加资源就为空列表
    for key, value in resource_list.items():
        if key in resource_context.keys() and value: 
            resource_context[key] = value 
    
    return render(request, 'show.html', context=resource_context)


# 查看个人课程
def ViewMyCourse(request):
    # 用户身份
    
    if request and request.session.get('is_login'):
        user_id =  request.session.get('user_id')
        course_list = Course.objects.filter(
            course_id__in=UserCourse.objects.filter(user_id=user_id, state=True).values_list('course_id', flat=True)
        ).order_by('course_id')
    else:
        # request.session.get('is_login')): # 游客身份
        course_list = []
    
    print(course_list)
    paginator = Paginator(course_list, 15)
    
    page_number = int(request.GET['page']) if request.GET.get('page') else 1
    page_obj = paginator.get_page(page_number)
    
    print("执行结束")
    return render(request, template_name='mycourse.html', context={'page_obj': page_obj})


def ReceiveLikeCourse(request):
    '''判断是游客还是用户，接受用户上传的表单数据'''
    if request and request.method == 'POST':
        if request.session.get('is_login'): # 用户
            user_id = request.session.get('user_id')
            user_name = request.session['username']
            form_data = request.POST
            
            # 处理对数据库数据的更改
            opt = form_data.get('course-opt') # querydict多值字典，get返回第一个 
            course_int_id = int(form_data.get('course-id')) # 隐藏域传入的课程id
            
            if opt == 'like':
                state = True
            elif opt == 'dislike':
                state = False
            else:
                pass
            
            
            
            user = User.objects.get(u_id=user_id)
            course = Course.objects.get(id=course_int_id)
            origin = UserCourse.objects.filter(user=user_id, course=course.course_id) # 表中有记录
        
                
            if len(origin) > 0:
                origin[0].state=state # 表中有自增字段，不可以使用update更新
                origin[0].save()
                course = origin[0].course 
                print("修改对课程的喜欢")
            else:
                user_course = UserCourse.objects.create(user=user, course=course, state=state)
                user_course.save()
                course = user_course.course
                print("创建成功")
                
            # 更改课程的喜欢人数
            if course.user_num is None: #空值
                course.user_num = 1
            else:
                course.user_num += (1 if state else 0)
            course.save()
            print("更改course表课程的喜欢人数")
            
            referer = request.META['HTTP_REFERER']  # 来路
            return HttpResponseRedirect(redirect_to=referer) 
            
        else:
            return HttpResponseRedirect(redirect_to='/login/')
    else:
        return HttpResponse('GET非法请求, 请求方法应为POST')
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



# --------------------------
def get_search_course(request):
    ss=request.GET.get('search')#获取搜索的关键词
    search_course = Course.objects.filter(name__icontains=ss)#获取到搜索关键词通过标题进行匹配
    return search_course
    
# 搜索页
r_search = PageResource('search')
page_manager.set_page_resource('search', r_search) # 添加search页面资源
@view_with_resource('search')
def ViewSearch(request, **kwargs):
    
    # 共有资源
    r_search.thread_set_resource('allcategory', func=get_allcategory)
    r_search.thread_set_resource('hot_recommend', func=get_hot_recommend)
    r_search.thread_set_resource('tags', func=get_tags)
    
    # 页面独有资源
    r_search.thread_set_resource('search_course', func=get_search_course)
    
    # 通知，进程加载资源完成
    r_search.notify()
    
    resource_list = kwargs['resource_list'] if kwargs.get('resource_list') else None
    
    resource_context = {'allcategory': [],
                'hot_recommend': [],
                'tags': [],
                'search_course': [],
                'ss': [],
                'page_obj': [],
                }
    # 如果没有添加资源就为空列表
    for key, value in resource_list.items():
        if key in resource_context.keys() and value: 
            resource_context[key] = value    

    course_list = resource_context['search_course'] # 返回的课程列表
    paginator = Paginator(course_list, 15)
    
    page_number = int(request.GET['page']) if request.GET.get('page') else 1
    
    page_obj = paginator.get_page(page_number) # 获取当前页码的记录

    resource_context['page_obj'] = page_obj
    resource_context['ss'] = request.GET.get('search') #获取搜索的关键词
    return render(request, 'search.html', context=resource_context)

# 关于页
def ViewAbout(request):
    allcategory = Category.objects.all()
    return render(request, 'page.html',locals())

