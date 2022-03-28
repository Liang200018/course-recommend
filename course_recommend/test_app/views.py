from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import NameForm
# Create your views here.

def hello(request):
    info = "hello world"
    return HttpResponse(info)

def get_name(request):
    # 接受表单
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            # 处理 form.cleaned_data
            # ...............
            return HttpResponseRedirect('/test_app/hello')
    else:
        # 发布表单
        form = NameForm()
    
    context = {'form': form}
    return render(request, 'name.html', context=context)

if __name__ == "__main__":
    hello()