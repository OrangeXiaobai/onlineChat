import openai
from django.db.models import Count
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from answer.models import Answer, Statistics
from answer.serializers import AnswerSerializer, StatisticsSerializer
from user.models import CustomUser, UserStatus
from user.serializers import UserSerializer, UserStatusSerializer
from user_agents import parse


# /api/users/register/
@api_view(['POST'])  # @api_view 装饰器主要用于指定视图支持的 HTTP 请求方法，并自动处理请求数据的解析和响应的格式化
def register(request):
    serializer = UserSerializer(data=request.data)  # 接收请求数据并通过 UserSerializer 进行验证
    if serializer.is_valid():  # 验证数据有效
        serializer.save()  # 将数据保存到与序列化器关联的模型的数据库表中
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # 返回序列化数据和状态码 201
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 返回错误信息和状态码 400


# /api/users/login/
@api_view(['POST'])
def login(request):
    # 从请求数据中获取用户对象字段
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    password = request.data.get('password')

    user = None
    # 根据 phone_number 或 email 查找用户
    if phone_number:
        user = CustomUser.objects.filter(phone_number=phone_number).first()
    elif email:
        user = CustomUser.objects.filter(email=email).first()

    if user and user.check_password(password):  # 验证用户密码
        if not user.status:
            return Response({'error': '此用户禁止登陆，请联系管理员'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'message': '登录成功'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '无效的凭证'}, status=status.HTTP_401_UNAUTHORIZED)


# /api/users/get/
@api_view(['GET'])
def get_users(request):
    users = CustomUser.objects.all()  # 查找左所有
    serializer = UserSerializer(users, many=True)  # 序列化多个用户实例
    return Response(serializer.data)


# /api/users/delete/id/
@api_view(['DELETE'])
def delete_user(request, pk):  # pk：从 URL 路由中获取的路径参数，用于查找特定的用户
    try:
        user = CustomUser.objects.get(pk=pk)  # 根据主键查找用户
    except CustomUser.DoesNotExist:
        return Response({'error': '用户未找到'}, status=status.HTTP_404_NOT_FOUND)
    user.delete()
    return Response({'message': '删除成功'}, status=status.HTTP_204_NO_CONTENT)


# /api/users/update/id/
@api_view(['PUT'])
def update_user(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': '用户未找到'}, status=status.HTTP_404_NOT_FOUND)

    # 用现有的用户实例 user 和请求数据 request.data 初始化序列化器 UserSerializer。
    # 列化器将用新的数据更新现有的用户实例。
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 初始化 OpenAI 客户端
client = openai.OpenAI(
    api_key="sk-1Ulnk2ppYDcodGQEfKdf9FgMbalz4zXuNZ1P7ie1SXRZHph3",
    base_url="https://api.moonshot.cn/v1",
)


# api/answer/get?keywords=keywords1,keywords2
@api_view(['GET'])  # DRF 的装饰器，指定请求方式 GET
def get_answer(request):
    # 获取请求中的关键词参数
    keywords = request.GET.get('keywords')
    if keywords:  # 输入了关键词
        keywords_list = keywords.split(',')  # 关键词分割为列表
        # 根据关键字查询数据库
        responses = Answer.objects.filter(keywords__icontains=keywords_list[0])
        if responses.exists():  # 如果数据库里有数据
            for keyword in keywords_list[1:]:
                responses = responses.filter(keywords__icontains=keyword)
            # 创建一个 AnswerSerializer 的实例，传入参数 many=True 表示序列化多个对象
            serializer = AnswerSerializer(responses, many=True)
            # 使用 Response 对象将序列化的数据作为响应返回
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:  # 如果数据库里没有数据，调用AI
            try:
                # 调用 Kimi API
                completion = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "user", "content": f"一句话介绍 {keywords_list} "}
                    ],
                    temperature=0.3,
                )
                ai_response = completion.choices[0].message.content

                # 将 Kimi AI 的回答存储到数据库中
                new_response = Answer(
                    keywords=keywords,
                    response_type='text',  # 假设是文本类型
                    content=ai_response,
                    ai_answer=True,
                )
                new_response.save()

                # 再重新取出来
                responses = Answer.objects.filter(keywords__icontains=keywords)

                serializer = AnswerSerializer(responses, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except openai.RateLimitError:
                return Response({'error': '关键词不为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 关键词没有，异常
    return Response({'error': '关键词不为空'}, status=status.HTTP_400_BAD_REQUEST)


# /api/answer/add
@api_view(['POST'])
def add_answer(request):
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# /api/answer/update
@api_view(['PUT'])
def update_answer(request):
    try:
        response = Answer.objects.get(id=request.data['id'])
    except Answer.DoesNotExist:
        return Response({'error': 'Response not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AnswerSerializer(response, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# /api/answer/delete
@api_view(['DELETE'])
def delete_answer(request):
    try:
        response = Answer.objects.get(id=request.data['id'])
        response.delete()
        return Response({'message': '删除成功'}, status=status.HTTP_200_OK)
    except Answer.DoesNotExist:
        return Response({'error': '未找到数据'}, status=status.HTTP_404_NOT_FOUND)


# /api/answer/statistics
@api_view(['GET'])
def statistics_get(request):
    userdata = Statistics.objects.all()
    serializer = StatisticsSerializer(userdata, many=True)
    return Response(serializer.data)


# /api/answer/process
@api_view(['GET'])
def process_get(request):
    # 统计 IP 来源
    ip_statistics = Statistics.objects.values('ip_address').annotate(
        count=Count('ip_address')).order_by('-count')

    # 统计浏览器类型
    browser_statistics = Statistics.objects.values('browser_type').annotate(
        count=Count('browser_type')).order_by('-count')
    # 裁剪，只保留浏览器名称 google等
    for stat in browser_statistics:
        browser_type = parse(stat['browser_type']).browser.family
        stat['browser_type'] = browser_type

    # 统计高频短语
    keyword_statistics = Statistics.objects.values('keyword').annotate(
        count=Count('keyword')).order_by('-count')

    # 按时间段统计用户输入的数据
    time_statistics = Statistics.objects.extra(select={'day': 'date(timestamp)'}).values('day').annotate(
        count=Count('id')).order_by('-day')

    data = {
        'ip_statistics': list(ip_statistics),
        'browser_statistics': list(browser_statistics),
        'keyword_statistics': list(keyword_statistics),
        'time_statistics': list(time_statistics),
    }

    return Response(data, status=status.HTTP_200_OK)


# /api/users/status
@api_view(['GET'])
def get_user_status(request):
    userstatus = UserStatus.objects.all()
    serializer = UserStatusSerializer(userstatus, many=True)
    return Response(serializer.data)
