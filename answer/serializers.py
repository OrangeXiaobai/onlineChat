from rest_framework import serializers

from .models import Answer, Statistics


# 对 Answer 模型进行序列化和反序列化的规则
# 基本的 CRUD 操作，模型的字段与序列化器的字段之间没有特殊的映射或转换需求，
# 直接使用 ModelSerializer 的默认方法，不需要自定义
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer  # 指定模型
        fields = '__all__'  # 指定字段（全部）


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = '__all__'
