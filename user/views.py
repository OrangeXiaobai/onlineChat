import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from user.forms import RegisterForm, MessageForm
from user.models import Message


def index(request):
    return render(request, 'index.html')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # 指定登录页面的模板路径
    authentication_form = AuthenticationForm  # 指定用于用户登录的表单类，默认为 AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=username, password=password)  # 验证用户

        if user is not None:
            if not user.status:
                return HttpResponse('此用户禁止登录，请联系管理员', status=403)
            login(self.request, user)  # 调用 login 函数进行用户登录
            return super().form_valid(form)  # 调用父类的 form_valid 方法继续处理表单。
        else:
            return self.form_invalid(form)  # 处理无效表单





# 用户注册
def RegisterView(request):
    if request.method == 'POST':  # 处理 post(表单提交是 post) 请求
        form = RegisterForm(request.POST)  # 用户填写的数据实例化表单对象
        if form.is_valid():  # 验证表单
            # 注册请求
            response = requests.post(f'{settings.BASE_URL}/api/users/register/', data=form.cleaned_data)

            if response.status_code == 201:
                messages.success(request, '注册成功')
                return redirect('login')  # 重定向
            else:
                messages.error(request, response.json().get('error', '注册失败'))
    else:  # 进入到页面时，或其他非 post 请求
        form = RegisterForm()  # 空表单对象
    return render(request, 'register.html', {'form': form})


# 私信首页
def user_online(request):
    customuser = requests.get(f'{settings.BASE_URL}/api/users/get')
    customuser_data = customuser.json()
    userstatus = requests.get(f'{settings.BASE_URL}/api/users/status')
    userstatus_data = userstatus.json()

    customuser_dict = {user['id']: user['phone_number'] for user in customuser_data}

    for user in userstatus_data:
        user_id = user.get('user', None)

        if user_id in customuser_dict:
            user['phone_number'] = customuser_dict[user_id]
    return render(request, 'user_online.html', {'userstatus': userstatus_data})


User = get_user_model()


def message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(# Django Q 对象：构建复杂的查询条件
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('userchat', user_id=user_id)
    else:
        form = MessageForm()
    return render(request, 'user_chat.html', {'other_user': other_user, 'messages': messages, 'form': form})
