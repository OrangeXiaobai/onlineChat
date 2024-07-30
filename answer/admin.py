from django.contrib import admin

from answer.models import Answer, Statistics


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'keywords', 'response_type', 'content', 'ai_answer')


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'browser_type', 'keyword', 'timestamp')

