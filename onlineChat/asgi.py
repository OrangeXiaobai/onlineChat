import os

from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from user import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineChat.settings')

application = ProtocolTypeRouter(  # ProtocolTypeRouter 是 Channels 提供的一个路由器，根据协议类型将请求分发给相应的处理程序
    {
        "http": get_asgi_application(),  # 对于 HTTP 请求，get_asgi_application 返回标准的 Django ASGI 应用程序处理 HTTP 请求。
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
