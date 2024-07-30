from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from user.models import UserStatus

User = get_user_model()


@receiver(user_logged_in)  # user_logged_in:用户登录时发送信号
def user_logged_in_handler(sender, request, user, **kwargs):
    # 创建一个 UserStatus 对象，与当前用户关联
    user_status, created = UserStatus.objects.get_or_create(user=user)
    user_status.is_online = True  # 将用户状态设置为在线
    user_status.ip_address = request.META.get('REMOTE_ADDR')  # 获取并记录用户的 IP 地址
    user_status.save()  # 保存到数据库


@receiver(user_logged_out)  # user_logged_in:用户登出时发送信号
def user_logged_out_handler(sender, request, user, **kwargs):
    user_status = UserStatus.objects.get(user=user)  # # 获取与当前用户关联的对象
    user_status.is_online = False  # 将用户状态设置为下线
    user_status.save()  # 保存到数据库
