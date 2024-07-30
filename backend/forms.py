from django import forms


# 修改用户表单
class EditUserForm(forms.Form):
    phone_number = forms.CharField(label='Phone Number', max_length=20)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    status = forms.ChoiceField(label='Status',
                               choices=[(True, 'Active'), (False, 'Inactive')])


# 增加应答表单
class AddAnswerForm(forms.Form):
    keywords = forms.CharField(max_length=100, required=True, label="Keywords")
    response_type = forms.ChoiceField(required=True, label="Response Type",
                                      choices=[('text', 'Text'), ('image', 'Image'), ('link', 'Link')])
    content = forms.CharField(widget=forms.Textarea, required=False, label="Content")
    image = forms.ImageField(required=False, label="Image")

    # 验证逻辑
    def clean(self):
        cleaned_data = super().clean()  # 返回的已清理数据
        response_type = cleaned_data.get("response_type")
        content = cleaned_data.get("content")
        image = cleaned_data.get("image")

        if response_type == 'text' or response_type == 'link':
            if not content:
                raise forms.ValidationError("没有文字")
        elif response_type == 'image':
            if not image:
                raise forms.ValidationError("没有图片")

        return cleaned_data


# 修改应答表单
class EditAnswerForm(forms.Form):
    keywords = forms.CharField(label='Keywords', max_length=255)
    response_type = forms.ChoiceField(label='Response Type',
                                      choices=[('text', 'Text'), ('image', 'Image'), ('link', 'Link')])
    content = forms.CharField(label='Content', max_length=255, required=False)
    image = forms.ImageField(label='Image', required=False)
    ai_answer = forms.ChoiceField(label='AI Answer', required=False,
                                  choices=[(True, 'True'), (False, 'False')])
