from django.urls import path
from .views import home, registro, custom_login_view, productos, carrito, confirmar_pedido, pedidos_cliente
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Vistas para usuarios no registrados
    path('', home, name='home'),
    path('registro/', registro, name='registro'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Vista de productos
    path('productos/', productos, name='productos'),
   
    # Vistas para usuarios registrados
    path('carrito/', carrito, name='carrito'),
    path('carrito/confirmar/', confirmar_pedido, name='confirmar_pedido'),
    path('pedidos/', pedidos_cliente, name='pedidos_cliente'),
]


