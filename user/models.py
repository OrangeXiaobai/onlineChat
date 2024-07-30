from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# 替代 Django 内置的用户模型
class CustomUserManager(BaseUserManager):  # 用于管理 CustomUser 模型中的用户创建和管理操作。
    def create_user(self, phone_number, email, password=None):
        # 检查必填项
        if not phone_number:
            raise ValueError('电话号码为必填项')
        if not email:
            raise ValueError('邮件为必填项')
        # 创建用户
        user = self.model(
            phone_number=phone_number,
            email=self.normalize_email(email),
        )

        user.set_password(password)  # 处理密码的哈希化
        user.save(using=self._db)  # 将用户保存到数据库
        return user

    def create_superuser(self, phone_number, email, password=None):
        user = self.create_user(  # 创建普通用户
            phone_number=phone_number,
            email=email,
            password=password,
        )
        user.is_admin = True  # 设置管理员权限
        user.save(using=self._db)
        return user  # 返回超级用户


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    status = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    objects = CustomUserManager()  # 将 CustomUserManager 作为默认的管理器

    USERNAME_FIELD = 'phone_number'  # 用于登录的用户名字段
    REQUIRED_FIELDS = ['email']  # 其他必填字段

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):  # 检查用户是否有特定权限
        return self.is_admin

    def has_module_perms(self, app_label):  # 检查用户是否有访问应用的权限
        return self.is_admin


class UserStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # 1对多
    is_online = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
