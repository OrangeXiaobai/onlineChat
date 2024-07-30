from django import forms


class KeywordForm(forms.Form):
    keywords = forms.CharField(label='关键词', max_length=255, help_text='输入1~3个关键词，用逗号隔开')

