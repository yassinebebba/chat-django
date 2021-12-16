from django.urls import re_path
from .consumers import ChatConsumer
from .consumers import UserAuthorizationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/(?P<access_token>.+)/$', UserAuthorizationConsumer.as_asgi()),
]
