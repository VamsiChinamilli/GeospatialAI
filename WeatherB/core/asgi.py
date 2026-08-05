import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings",
)

from django.core.asgi import get_asgi_application
from core_next.utils.model_loader import ModelLoader

try:
    print("🚀 Preloading AI models...")
    ModelLoader.load_all()
    print("✅ AI models preloaded.")
except Exception as exc:
    print(f"❌ Failed to preload AI models: {exc}")


django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from core_next.routing import urlpatterns as websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,

        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)