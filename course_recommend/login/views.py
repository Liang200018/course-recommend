from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from course.models import User
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

def logout(request):
    context = {}
    # 如果不是登陆状态，无法登出
    if request.session.get('is_login'):
        request.session.flush()
    # 返回到登录界面
    return HttpResponseRedirect('/login/')