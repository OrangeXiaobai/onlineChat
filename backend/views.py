import io
import os

import pandas as pd
import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from matplotlib import pyplot as plt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser

from answer.models import Answer, Statistics
from backend.forms import EditUserForm, AddAnswerForm, EditAnswerForm
from user.models import CustomUser


# 用户列表
def user_admin(request):
    users = CustomUser.objects.all()
    return render(request, 'user_admin.html', {'users': users})


# 修改用户
def user_edit(request, id):  # id 代表用户id。此参数从 URL 路径中获取，用于查询特定的用户
    user = get_object_or_404(CustomUser, id=id)  # 从数据库中获取要编辑的用户。如果用户不存在，返回404错误
    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            status = form.cleaned_data['status']

            data = {
                'phone_number': phone_number,
                'email': email,
                'password': password,
                'status': status,
            }

            response = requests.put(f'{settings.BASE_URL}/api/users/update/{id}/', data=data)

            if response.status_code == 200:
                messages.success(request, '用户信息修改成功')
                return redirect('user_admin')
            else:
                messages.error(request, response.json().get('error', '用户信息修改失败'))
    else:
        form = EditUserForm(initial={
            'phone_number': user.phone_number,
            'email': user.email,
            'status': user.status
        })
    return render(request, 'user_edit.html', {'form': form, 'user_id': id})


# 删除用户
def user_delete(request, id):
    response = requests.delete(f'{settings.BASE_URL}/api/users/delete/{id}/')

    if response.status_code == 204:
        messages.success(request, '用户删除成功')
    else:
        messages.error(request, response.json().get('error', '用户删除失败'))

    return redirect('user_admin')


# 应答列表
def answer_admin(request):
    answers = Answer.objects.all()
    return render(request, 'answer_admin.html', {'answers': answers})


# 增加应答
def answer_add(request):
    if request.method == 'POST':
        form = AddAnswerForm(request.POST, request.FILES)  # request.FILES：上传的文件数据

        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            response_type = form.cleaned_data['response_type']
            content = form.cleaned_data['content']

            if response_type == 'text' or response_type == 'link':
                data = {
                    'keywords': keywords,
                    'response_type': response_type,
                    'content': content
                }
                response = requests.post(f'{settings.BASE_URL}/api/answer/add', data=data)
            elif response_type == 'image':
                image = form.cleaned_data['image']
                # 拼接图片存储路径：/static/images/name
                image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', image.name)
                # 以二进制写模式 (wb+) 打开 image_path 的文件
                with open(image_path, 'wb+') as destination:
                    # 分块读取上传的图片文件
                    for chunk in image.chunks():  # image.chunks()：将图片文件分成小块，以避免一次性读取大文件导致内存不足问题
                        destination.write(chunk)  # 将每个块写入
                data = {
                    'keywords': keywords,
                    'response_type': response_type,
                    'content': f'/static/images/{image.name}'
                }
                response = requests.post(f'{settings.BASE_URL}/api/answer/add', data=data)

            if response.status_code == 201:
                messages.success(request, '添加成功')
                return redirect('answer_admin')
            else:
                messages.error(request, response.json().get('error', '添加失败'))
    else:
        form = AddAnswerForm()
    return render(request, 'answer_add.html', {'form': form})


# 修改应答
def answer_edit(request, id):
    answer = get_object_or_404(Answer, id=id)
    if request.method == 'POST':
        form = EditAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            response_type = form.cleaned_data['response_type']
            content = form.cleaned_data['content']
            ai_answer = form.cleaned_data['ai_answer']

            if response_type == 'text' or response_type == 'link':
                data = {
                    'id': id,
                    'keywords': keywords,
                    'response_type': response_type,
                    'content': content,
                    'ai_answer': ai_answer
                }
                response = requests.put(f'{settings.BASE_URL}/api/answer/update', data=data)
            elif response_type == 'image':
                if answer.content:  # 旧文件路径
                    # 将 /static/ 前缀移除，并将所有的 / 替换为 \
                    answer.content = answer.content.replace('/static/', '')
                    answer.content = answer.content.replace('/', '\\')
                    image_path = os.path.join(settings.STATICFILES_DIRS[0], answer.content)
                    if os.path.exists(image_path):  # os.path.exists 检查文件是否存在
                        os.remove(image_path)  # 删除旧文件

                image = form.cleaned_data['image']
                # 保存新文件
                image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                data = {
                    'id': id,
                    'keywords': keywords,
                    'response_type': response_type,
                    'content': f'/static/images/{image.name}',
                    'ai_answer': ai_answer
                }
                response = requests.put(f'{settings.BASE_URL}/api/answer/update', data=data)

            if response.status_code == 200:
                messages.success(request, '修改成功')
                return redirect('answer_admin')
            else:
                messages.error(request, response.json().get('error', '修改失败'))
    else:
        form = EditAnswerForm(initial={  # initial：预填充表单字段
            'keywords': answer.keywords,
            'response_type': answer.response_type,
            'content': answer.content,
            'ai_answer': answer.ai_answer
        })
    return render(request, 'answer_edit.html', {'form': form, 'answer': answer})


# 删除应答
def answer_delete(request, id):
    answer = get_object_or_404(Answer, id=id)
    if answer.response_type == 'image' and answer.content:
        # 删除图片
        answer.content = answer.content.replace('/static/', '')
        answer.content = answer.content.replace('/', '\\')
        image_path = os.path.join(settings.STATICFILES_DIRS[0], answer.content)
        if os.path.exists(image_path):
            os.remove(image_path)

    response = requests.delete(f'{settings.BASE_URL}/api/answer/delete', data={'id': id})
    if response.status_code == 200:
        messages.success(request, '删除成功')
    else:
        messages.error(request, response.json().get('error', '删除失败'))
    return redirect('answer_admin')


# 数据统计首页
def statistics_admin(request):
    data = Statistics.objects.all()
    return render(request, 'statistics_admin.html', {'response': data})


# 导出用户为 excel
def export_users_to_excel(request):
    response = requests.get(f'{settings.BASE_URL}/api/users/get')
    data = response.json()

    output = io.BytesIO()  # 用 BytesIO 来创建一个字节流对象，类似于文件对象，但它将数据保存在内存中，而不是磁盘上。
    with pd.ExcelWriter(output, engine='openpyxl') as writer:  # 使用 pandas.ExcelWriter 将数据写入 output
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Users', index=False)

    output.seek(0)  # 重置指针

    # 创建响应对象
    # -HttpResponse：用于生成HTTP响应对象。
    # -output：作为响应的内容，即生成的Excel文件。
    # -content_type：指定响应的内容类型为Excel文件。application/vnd.openxmlformats-officedocument.spreadsheetml.sheet 是Excel文件的MIME类型。
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # 设置响应头：
    # -Content-Disposition：HTTP响应头之一，告诉浏览器如何处理响应内容。attachment 表示提示浏览器下载文件而不是直接显示它。
    # -filename=users.xlsx：指定下载文件的名称为 users.xlsx。
    response['Content-Disposition'] = 'attachment; filename=users.xlsx'
    return response


# 从 excel 导入用户数据
@parser_classes([FileUploadParser])  # 指定这个视图使用 FileUploadParser 解析器来处理文件上传
def import_users_from_excel(request):
    if 'file' in request.FILES:  # 检查请求中是否包含文件
        file_obj = request.FILES['file']
        df = pd.read_excel(file_obj)
    else:
        messages.error(request, '文件为空')
        return redirect('user_admin')

    for index, row in df.iterrows():
        data = {
            'phone_number': row['phone_number'],
            'email': row['email'],
            'password': row['password'],
            'status': row['status'],
        }
        response = requests.post(f'{settings.BASE_URL}/api/users/register/', data=data)
        if response.status_code != 201:
            messages.error(request, response.json().get('error', '导入失败'))
            return redirect('user_admin')

    messages.success(request, '导入成功')
    return redirect('user_admin')


# 导出统计数据为 excel
def export_statistics_to_excel(request):
    response = requests.get(f'{settings.BASE_URL}/api/answer/process')
    data = response.json()

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_ip = pd.DataFrame(data['ip_statistics'])
        df_browser = pd.DataFrame(data['browser_statistics'])
        df_keyword = pd.DataFrame(data['keyword_statistics'])
        df_time = pd.DataFrame(data['time_statistics'])

        df_ip.to_excel(writer, sheet_name='IP Statistics', index=False)
        df_browser.to_excel(writer, sheet_name='Browser Statistics', index=False)
        df_keyword.to_excel(writer, sheet_name='Keyword Statistics', index=False)
        df_time.to_excel(writer, sheet_name='Time Statistics', index=False)

    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=statistics.xlsx'
    return response


# 导出统计数据为图片
def export_statistics_to_image(request):
    response = requests.get(f'{settings.BASE_URL}/api/answer/process')
    data = response.json()

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体

    df_ip = pd.DataFrame(data['ip_statistics'])
    df_browser = pd.DataFrame(data['browser_statistics'])
    df_keyword = pd.DataFrame(data['keyword_statistics'])
    df_time = pd.DataFrame(data['time_statistics'])

    df_ip.plot(kind='bar', x='ip_address', y='count', ax=axs[0, 0], title='IP Statistics')
    df_browser.plot(kind='bar', x='browser_type', y='count', ax=axs[0, 1], title='Browser Statistics')
    df_keyword.plot(kind='bar', x='keyword', y='count', ax=axs[1, 0], title='Keyword Statistics')
    df_time.plot(kind='line', x='day', y='count', ax=axs[1, 1], title='Time Statistics')

    plt.tight_layout()
    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)

    response = HttpResponse(output, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename=statistics.png'
    return response
