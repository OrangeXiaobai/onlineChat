from django import forms
from .models import CustomUser, Message


# 用户注册表单
class RegisterForm(forms.ModelForm):  # 继承自 forms.ModelForm：用于创建与模型 CustomUser 相关的表单。
    password = forms.CharField(widget=forms.PasswordInput)  # 自定义密码字段，并指定密码以隐藏形式显示。

    class Meta:
        model = CustomUser  # 关联模型
        fields = ['phone_number', 'email', 'password']  # 显示的字段

    # 自定义密码验证逻辑
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6 or len(password) > 20:
            raise forms.ValidationError('密码长度必须在6到20个字符之间')
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            raise forms.ValidationError('密码必须包含字母和数字的组合')
        return password


#  私信表单
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
