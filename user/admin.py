from django.contrib import admin

from user.models import CustomUser, UserStatus, Message


@admin.register(CustomUser)  # 使用装饰器将 CustomUserAdmin 类注册为 CustomUser 模型的管理界面。
class CustomUserAdmin(admin.ModelAdmin):  # 继承自 admin.ModelAdmin 类，用于配置 CustomUser 模型在 admin 界面中的显示和行为。
    list_display = ('id', 'phone_number', 'email', 'status', 'is_staff')  # ist_display 属性，指定在 CustomUser 管理页面中显示的字段


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'ip_address')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp')
