from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import mote.chat.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            mote.chat.routing.websocket_urlpatterns
        )
    ),
})


