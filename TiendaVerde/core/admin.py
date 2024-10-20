from django.contrib import admin
from .models import Producto, Pedido, Carrito, CarritoItem

# Registrar los modelos en el administrador
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
