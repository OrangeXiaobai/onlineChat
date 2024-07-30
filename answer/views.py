import io
import os

import requests
from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser

from answer.forms import KeywordForm
from answer.models import Statistics


# 获取客户端 IP
def get_client_ip(request):
    # 从 HTTP_X_FORWARDED_FOR 头部中获取 IP 地址，因为有些代理服务器会将客户端真实 IP 存在这个头部。
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:  # 直接从 REMOTE_ADDR 获取 IP 地址。
        ip = request.META.get('REMOTE_ADDR')
    return ip


# 获取浏览器类型
def get_browser_type(request):
    # 从请求的 HTTP_USER_AGENT 头部中获取浏览器的标识信息，用于识别浏览器类型
    return request.META.get('HTTP_USER_AGENT', 'unknown')


def chat(request):
    if request.method == 'POST':  # 处理表单请求
        form = KeywordForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']

            # 记录用户请求数据
            ip_address = get_client_ip(request)
            browser_type = get_browser_type(request)
            Statistics.objects.create(ip_address=ip_address, browser_type=browser_type, keyword=keywords)

            try:
                response = requests.get(f'{settings.BASE_URL}/api/answer/get?keywords={keywords}')
                if response.status_code == 200:
                    data = response.json()  # 转为json
                    return render(request, 'chat.html', {'form': form, 'answer': data})
                else:
                    return render(request, 'chat.html', {
                        'form': form,
                        'error_message': '无法从API获取数据',
                    })
            except requests.exceptions.RequestException as e:
                return render(request, 'chat.html', {
                    'form': form,
                    'error_message': f'请求失败: {e}',
                })
    else:
        form = KeywordForm()
    return render(request, 'chat.html', {'form': form})


# 图片处理
@parser_classes([FileUploadParser])
def export_image_with_logo(request):
    if 'file' in request.FILES:
        image_file = request.FILES['file']

        # 打开图片和logo图片
        image = Image.open(image_file)
        logo = Image.open(os.path.join(settings.STATICFILES_DIRS[0], 'images/logo.png'))

        # 获取logo的尺寸
        logo_width, logo_height = logo.size

        # pillow的坐标：图片左上角为坐标原点，向右为x轴，向下为y轴
        # 设置logo的位置为图片A的右上角
        image_width, image_height = image.size
        position = (image_width - logo_width, 0)

        # 原图或 logo 包含透明区域，直接在原图上粘贴可能会导致出错。
        # 创建一个新的空白图像（特别是 RGBA 模式）可以更好地处理透明度问题。
        new_image = Image.new("RGB", (image_width, image_height))
        new_image.paste(image, (0, 0))
        new_image.paste(logo, position)

        # 将处理后的图片保存到字节流
        output = io.BytesIO()
        new_image.save(output, format='PNG')
        output.seek(0)

        # 返回图片文件响应
        response = HttpResponse(output, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename=processed_{image_file.name}'
        print(response)
        return response
    else:
        messages.error(request, '文件为空')
        return redirect('chat')
