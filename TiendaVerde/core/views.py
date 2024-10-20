from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import Carrito, Producto, Pedido, CarritoItem
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


# Views para usuarios no registrados.

def home(request):
    titulo= "Tienda Verde"
    data = {
        "titulo": titulo
    }
    return render(request, "core/home.html", data)


def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Asignar el usuario al grupo "Clientes"
            clientes_group = Group.objects.get(name='Clientes')  # Buscar el grupo Clientes
            user.groups.add(clientes_group)  # Asignar al usuario al grupo

            # Autenticar e iniciar sesión al usuario después del registro
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'tienda/registro.html', {'form': form})



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
            carrito_item.cantidad += 1
            carrito_item.save()

            return redirect('carrito')
        else:
            return redirect('%s?next=%s' % (reverse('login'), request.path))

    return render(request, 'core/productos.html', {'productos': productos_list})


# Views para clientes registrados.

@login_required
def carrito(request):
    carrito = Carrito.objects.get(cliente=request.user)
    
    if request.method == 'POST':
        # Actualizar o eliminar productos del carrito
        for item in carrito.carritoitem_set.all():
            cantidad = request.POST.get(f'cantidad_{item.producto.id}')
            if cantidad == '0':
                item.delete()  # Eliminar el producto si la cantidad es 0
            else:
                item.cantidad = int(cantidad)
                item.save()

        return redirect('carrito')

    return render(request, 'tienda/carrito.html', {'carrito': carrito})

@login_required
def confirmar_pedido(request):
    carrito = Carrito.objects.get(cliente=request.user)
    if request.method == 'POST':
        # Crear un pedido a partir del carrito
        pedido = Pedido.objects.create(cliente=request.user, carrito=carrito, total=carrito.total)
        pedido.save()

        # Vaciar el carrito
        carrito.carritoitem_set.all().delete()

        return redirect('pedidos_cliente')

    return render(request, 'tienda/confirmar_pedido.html', {'carrito': carrito})

@login_required
def pedidos_cliente(request):
    pedidos = Pedido.objects.filter(cliente=request.user)
    return render(request, 'tienda/pedidos_cliente.html', {'pedidos': pedidos})