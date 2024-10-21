from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import Carrito, Producto, Pedido, CarritoItem
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from .models import Pedido

# Views para usuarios no registrados.

def home(request):
    titulo= "Tienda Verde"
    data = {
        "titulo": titulo
    }
    return render(request, "core/home.html", data)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Iniciar sesión automáticamente después del registro
            return redirect('home')  # Redirigir a la página principal después del registro
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})



def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
        else:
            # Si el formulario no es válido, mostrar los errores
            return render(request, 'core/login.html', {'form': form})
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})



def productos(request):
    productos_list = Producto.objects.all()  # Obtener todos los productos
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        
        if request.user.is_authenticated:
            carrito, created = Carrito.objects.get_or_create(cliente=request.user)
            carrito_item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)

            if not created:
                # Solo incrementamos la cantidad si el item ya existía
                carrito_item.cantidad += 1
            else:
                # Si el item es nuevo, lo iniciamos con una cantidad de 1
                carrito_item.cantidad = 1
                
            carrito_item.save()

            return redirect('carrito')
        else:
            return redirect('%s?next=%s' % (reverse('login'), request.path))

    return render(request, 'core/productos.html', {'productos': productos_list})

# Views para clientes registrados.

@login_required
def carrito(request):
    # Intenta obtener el carrito del usuario, si no existe, lo crea
    carrito, created = Carrito.objects.get_or_create(cliente=request.user)

    if request.method == 'POST':
        # Actualizar o eliminar productos del carrito
        for item in carrito.carritoitem_set.all():
            cantidad = request.POST.get(f'cantidad_{item.producto.id}')
            
            # Eliminar producto si se presiona el botón de eliminar
            if f'eliminar_{item.producto.id}' in request.POST:
                item.delete()
            else:
                # Actualizar la cantidad si no es 0
                if cantidad and int(cantidad) > 0:
                    item.cantidad = int(cantidad)
                    item.save()
                elif int(cantidad) == 0:
                    item.delete()  # Eliminar el producto si la cantidad es 0

        return redirect('carrito')

    # Calcular el total y los subtotales para cada item
    total = 0
    items_con_subtotal = []
    for item in carrito.carritoitem_set.all():
        subtotal = item.producto.precio * item.cantidad
        total += subtotal
        items_con_subtotal.append({
            'producto': item.producto,
            'cantidad': item.cantidad,
            'precio_unitario': item.producto.precio,
            'subtotal': subtotal
        })

    carrito.total = total
    carrito.save()

    return render(request, 'core/carrito.html', {'carrito': carrito, 'items_con_subtotal': items_con_subtotal, 'total': total})



@login_required
def confirmar_pedido(request):
    # Obtener el carrito del usuario
    try:
        carrito = Carrito.objects.get(cliente=request.user)
    except Carrito.DoesNotExist:
        # Si no hay carrito asociado, redirige al carrito vacío
        return redirect('carrito')

    # Verificar si el carrito no está vacío
    if not carrito.carritoitem_set.exists():
        return redirect('carrito')  # Redirige al carrito si está vacío

    if request.method == 'POST':
        # Crear el pedido solo si no existe un pedido para este carrito
        pedido = Pedido.objects.create(
            cliente=request.user,
            carrito=carrito,  # Asociar el carrito con el pedido
            total=carrito.total,
            estado='PEND',
        )

        # Vaciar el carrito anterior
        carrito.carritoitem_set.all().delete()

        # **No crear un nuevo carrito si ya existe uno**
        carrito.total = 0
        carrito.save()

        # Redirigir al historial de pedidos
        return redirect('pedidos_cliente')

    return render(request, 'core/confirmar_pedido.html', {'carrito': carrito})

@login_required
def pedidos(request):
    # Obtener los pedidos del usuario actual
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha')

    return render(request, 'core/pedidos.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    # Obtener el pedido específico del usuario
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    # Obtener los items del carrito asociados al pedido
    items = pedido.carrito.carritoitem_set.all()

    return render(request, 'core/detalle_pedido.html', {'pedido': pedido, 'items': items})