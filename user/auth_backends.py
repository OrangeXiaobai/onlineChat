from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


# 实现用户可以使用 phone_number 或 email 登录的功能
class PhoneOrEmailBackend(BaseBackend):  # BaseBackend 是 Django 的一个基本身份验证后端类
    # 用于验证用户身
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)  # 从 kwargs 中获取默认的用户名字段

        try:
            if '@' in username:
                user = UserModel.objects.get(email=username)
            else:
                user = UserModel.objects.get(phone_number=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self._user_can_authenticate(user):
            return user
        return None

    # 用于根据用户ID获取用户对象
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)  # 通过用户ID获取用户对象
        except UserModel.DoesNotExist:
            return None

    # 用于检查用户是否可以被认证
    def _user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)  # 获取用户的 is_active 属性
        return is_active or is_active is None  # 如果 is_active 为 True 或者用户模型中没有 is_active 属性，则返回 True，表示用户可以被认证
