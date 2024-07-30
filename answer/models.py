from django.db import models


class Answer(models.Model):
    id = models.AutoField(primary_key=True)  # 主键，自动递增
    keywords = models.CharField(max_length=255)
    # choices：第一个元素是实际存储在数据库中的值，第二个元素是在 Django 管理后台和表单中显示的友好名称。
    response_type = models.CharField(max_length=1000,
                                     choices=[('text', 'Text'), ('image', 'Image'), ('link', 'Link')])
    content = models.TextField()
    ai_answer = models.BooleanField(default=False)


class Statistics(models.Model):
    # GenericIPAddressField：用于存储 IPv4 或 IPv6 地址的字段。验证输入的 IP 地址，并将其存储为字符串。
    # -protocol 参数来限制存储的 IP 地址类型，例如 protocol='IPv4' 或 protocol='IPv6'
    # -如果未指定 protocol，则默认同时支持 IPv4 和 IPv6。
    ip_address = models.GenericIPAddressField()
    browser_type = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255)
    # DateTimeField:存储时间戳字段。精确到秒。
    # auto_now_add=True 参数指定在数据库创建新对象时自动设置字段值为当前日期和时间。
    timestamp = models.DateTimeField(auto_now_add=True)
