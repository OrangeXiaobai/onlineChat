from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from onlineChat import settings
from user.views import CustomLoginView, index

# 管理台
urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 首页
urlpatterns += [
    path('index/', index, name='index'),
    path('', RedirectView.as_view(url='/index')),
]

# api
urlpatterns += [
    path('api/', include('api.urls')),
]

# 内置登陆
urlpatterns += [
    path('accounts/login/', CustomLoginView.as_view(), name='login'),  # 使用自定义登录视图
    path('accounts/', include('django.contrib.auth.urls')),  # 提供了一组默认的 URL 模式
    # /accounts/login/：用户登录视图。--LoginView
    # /accounts/logout/：用户注销视图。--LogoutView
    # ······
]

urlpatterns += [
    path('user/', include('user.urls')),
    path('answer/', include('answer.urls')),
    path('backend/', include('backend.urls')),
]
