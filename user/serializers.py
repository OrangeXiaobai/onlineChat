from rest_framework import serializers
from .models import CustomUser, UserStatus


# CustomUser 的序列化器
# 继承自 serializers.ModelSerializer，用于将 CustomUser 模型实例序列化为 JSON 格式，以及从 JSON 格式反序列化为 CustomUser
class UserSerializer(serializers.ModelSerializer):
    # 元数据
    class Meta:
        model = CustomUser  # 指定模型
        fields = ['id', 'phone_number', 'email', 'password', 'status']  # 指定字段
        extra_kwargs = {'password': {'write_only': True}}  # 密码设为只写，不会被显示出来

    # 创建用户
    # 在 DRF 序列化器中，数据首先经过序列化器字段和验证器的检查。
    # 如果数据有效，它们将被存储在 validated_data 字典中，该字典包含了所有通过验证的字段和值
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],  # 从 validated_data 字典取出字段为 xxx 的值
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    # 更新用户
    # instance 表示当前要更新的对象
    def update(self, instance, validated_data):
        # 如果 validated_data 中包含 xxx，则使用新的 xxx；否则，保留现有的 xxx。
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.status = validated_data.get('status', instance.status)
        instance.save()  # 保存到数据库
        return instance


# 用户在线离线序列器
class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'
