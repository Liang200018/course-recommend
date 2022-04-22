from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from course.models import User, UserCourse


# Create your views here.

def index(request):
    context = {}
    return render(request, 'index.html', context=context)

def login(request):
    '''用户登录功能'''
    
    def validate(input_pwd, pwd):
        '''验证密码相同'''
        return input_pwd == pwd
        
    context = {}
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        if username and password: # 输入了账号密码
            record = User.objects.filter(name=username).first()
            print(record)
            if record and validate(password, record.password):                
                # session 记录用户数据
                request.session['is_login']=True
                request.session['user_id'] = record.u_id
                request.session['username'] = record.name
                request.session['items'] = {'test': 'test'}
                
                return HttpResponseRedirect('/index/')
            else:
                context['message'] = "账号或者密码错误"
                return render(request, 'login.html', context=context)
        else:
            context['message'] = "非法的请求"
            return render(request, 'login.html', context=context)
    return render(request, 'login.html')
    

def register(request):
    '''用户注册'''
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # 验证用户信息的有效性
        if username and password: # 输入了账号密码
            record = User.objects.filter(name=username).values('password').first()
            
            if record is None:
                u_id = username[:20] # 简单截取处理
                new_user = User.objects.create(u_id=u_id, name=username, password=password)
                new_user.save()
                context['message'] = "注册成功"
            else:
                context['message'] = "账号名已经存在"
        else:
            context['message'] = "非法的请求"
        
        return render(request, 'register.html', context=context)
    
    return render(request, 'register.html', context=context)



from course.views import icf_model


def logout(request):
    context = {}
    # 如果不是登陆状态，无法登出
    if request.session.get('is_login'):
        user_id = request.session['user_id']
        
        item_set = [course_id for course_id, state in request.session['items'].items() 
                    if state is True]
        # icf_model.model.writeToDB(userid, item_set=items_dict) # 将会话数据写入
        items = icf_model.model.getActiveItemByUserid(user_id, item_set=item_set)
        
        db_user_items = UserCourse.objects.filter(user_id=user_id, state=True).values_list('course_id', flat=True)
        db_user_items = [item for item in icf_model.model.Items] # 注意：数据库中存在的，并且是训练数据
        
        icf_model.model.updateIntByDB(items, db_user_items)
        icf_model.model.updateS()
        print("更新ICF")
        request.session.flush()
    # 返回到登录界面
    return HttpResponseRedirect('/login/')