from django.urls import path
from .views import home, registro, custom_login_view, productos, carrito, confirmar_pedido, pedidos, registro, detalle_pedido
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Vistas para usuarios no registrados
    path('', home, name='home'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),

    # Vista de productos
    path('productos/', productos, name='productos'),
   
    # Vistas para usuarios registrados
    path('carrito/', carrito, name='carrito'),
    path('carrito/confirmar/', confirmar_pedido, name='confirmar_pedido'),
    path('pedidos/', pedidos, name='pedidos_cliente'),
    path('pedidos/<int:pedido_id>/', detalle_pedido, name='detalle_pedido'),  # Detalle del pedido
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
