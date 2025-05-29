from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
from .models import Product, Brand, Category, Cart, CartItem, Order, OrderItem, UserLog
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from django.http import HttpResponseForbidden, FileResponse, HttpResponseRedirect
from abibas.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
import os
from django.conf import settings
from django.urls import reverse

# ---------------------------------------------
# Вьюхи приложения abibas
# Здесь реализована логика для пользователей, продавцов, склада и админки
# ---------------------------------------------

# --- Пользовательские вьюхи ---

def product_list(request):
    # Главная страница каталога. Фильтрация, сортировка, пагинация товаров.
    # Для всех пользователей.
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('abibas:dashboard')
    products = Product.objects.all()
    brands = Brand.objects.all()
    categories = Category.objects.all()
    
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(brand__name__icontains=search_query)
    
    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    
    paginator = Paginator(products, 9)  # Changed from 12 to 9 items per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'abibas/product_list.html', context)

def product_detail(request, pk):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('abibas:dashboard')
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'abibas/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    # добавить товар в корзину
    if request.user.is_staff or request.user.is_superuser:
        return redirect('abibas:dashboard')
    
    product = get_object_or_404(Product, id=product_id)
    selected_size = request.POST.get('size', product.size)
    
    # Проверяем наличие товара нужного размера
    if product.stock <= 0:
        messages.error(request, 'Товар отсутствует на складе')
        return redirect('abibas:product_detail', pk=product_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'Товар {product.name} (размер {selected_size}) добавлен в корзину')
    return redirect('abibas:cart')

@login_required
def cart(request):
    # корзина пользователя
    if request.user.is_staff or request.user.is_superuser:
        return redirect('abibas:dashboard')
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    
    for item in items:
        item.subtotal = item.product.price * item.quantity
    
    total = sum(item.subtotal for item in items)
    
    context = {
        'cart': cart,
        'items': items,
        'total': total,
    }
    return render(request, 'abibas/cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    # удаление из корзины
    if request.user.is_staff or request.user.is_superuser:
        return redirect('abibas:dashboard')
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('abibas:cart')

@login_required
def checkout(request):
    # оформление заказа
    if request.user.is_staff or request.user.is_superuser:
        return redirect('abibas:dashboard')
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.cartitem_set.all()
    
    if not items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('abibas:cart')
    
    for item in items:
        item.subtotal = item.product.price * item.quantity
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_amount=sum(item.subtotal for item in items),
            shipping_address=request.POST.get('shipping_address')
        )
        
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        cart.delete()
        
        UserLog.objects.create(user=request.user, action='order', info=f'Оформлен заказ #{order.id}')
        messages.success(request, 'Заказ успешно оформлен')
        return redirect('abibas:order_detail', pk=order.pk)
    
    total = sum(item.subtotal for item in items)
    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'abibas/checkout.html', context)

@login_required
def order_detail(request, pk):
    # детали заказа
    if request.user.role == 'admin':
        return redirect('abibas:dashboard')
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    order_items = order.orderitem_set.all()
    for item in order_items:
        item.item_total = item.price * item.quantity
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'abibas/order_detail.html', context)

@login_required
def order_list(request):
    # список заказов пользователя
    if request.user.role == 'admin':
        return redirect('abibas:dashboard')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'abibas/order_list.html', context)

def register(request):
    # регистрация
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserLog.objects.create(user=user, action='register', info='Регистрация нового пользователя')
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('abibas:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'abibas/register.html', {'form': form})

def user_login(request):
    # логин
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session.set_expiry(86400)  # 24 часа
                UserLog.objects.create(user=user, action='login', info='Вход пользователя')
                messages.success(request, 'Вход выполнен успешно!')
                if user.role == 'admin':
                    return redirect('abibas:dashboard')
                elif user.role == 'seller':
                    return redirect('abibas:seller_dashboard')
                elif user.role == 'warehouse':
                    return redirect('abibas:warehouse_dashboard')
                else:
                    return redirect('abibas:product_list')
    else:
        form = UserLoginForm()
    return render(request, 'abibas/login.html', {'form': form})

@login_required
def user_logout(request):
    # выход из аккаунта
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('abibas:product_list')

def is_admin(user):
    # проверка на админа
    return user.role == 'admin'

@user_passes_test(is_admin)
def dashboard(request):
    # главная страница админки
    if not is_admin(request.user):
        return HttpResponseForbidden('Доступ запрещён')
    return render(request, 'abibas/dashboard.html')

@user_passes_test(is_admin)
def user_list(request):
    # список пользователей (админ)
    users = User.objects.all()
    return render(request, 'abibas/dashboard_user_list.html', {'users': users})

@user_passes_test(is_admin)
def user_create(request):
    # создать пользователя (админ)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь создан!')
            return redirect('abibas:dashboard_user_list')
    else:
        form = UserCreationForm()
    return render(request, 'abibas/dashboard_user_form.html', {'form': form, 'title': 'Создать пользователя'})

@user_passes_test(is_admin)
def user_edit(request, user_id):
    # редактировать пользователя (админ)
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь обновлен!')
            return redirect('abibas:dashboard_user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'abibas/dashboard_user_form.html', {'form': form, 'title': 'Редактировать пользователя'})

@user_passes_test(is_admin)
def user_delete(request, user_id):
    # удалить пользователя (админ)
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь удален!')
        return redirect('abibas:dashboard_user_list')
    return render(request, 'abibas/dashboard_user_confirm_delete.html', {'user': user})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

@user_passes_test(is_admin)
def admin_product_list(request):
    # список товаров (админ)
    products = Product.objects.all()
    return render(request, 'abibas/dashboard_product_list.html', {'products': products})

@user_passes_test(is_admin)
def product_create(request):
    # создать товар (админ)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар создан!')
            return redirect('abibas:dashboard_product_list')
    else:
        form = ProductForm()
    return render(request, 'abibas/dashboard_product_form.html', {'form': form, 'title': 'Создать товар'})

@user_passes_test(is_admin)
def product_edit(request, product_id):
    # редактировать товар (админ)
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар обновлен!')
            return redirect('abibas:dashboard_product_list')
    else:
        form = ProductForm(instance=product)
    image_url = product.image.url if product.image else None
    return render(request, 'abibas/dashboard_product_form.html', {'form': form, 'title': 'Редактировать товар', 'image_url': image_url})

@user_passes_test(is_admin)
def product_delete(request, product_id):
    # удалить товар (админ)
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удален!')
        return redirect('abibas:dashboard_product_list')
    return render(request, 'abibas/dashboard_product_confirm_delete.html', {'product': product})

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

@user_passes_test(is_admin)
def admin_order_list(request):
    # список заказов (админ)
    orders = Order.objects.all()
    return render(request, 'abibas/dashboard_order_list.html', {'orders': orders})

@user_passes_test(is_admin)
def order_create(request):
    # создать заказ (админ)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ создан!')
            return redirect('abibas:dashboard_order_list')
    else:
        form = OrderForm()
    return render(request, 'abibas/dashboard_order_form.html', {'form': form, 'title': 'Создать заказ'})

@user_passes_test(is_admin)
def order_edit(request, order_id):
    # редактировать заказ (админ)
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ обновлен!')
            return redirect('abibas:dashboard_order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'abibas/dashboard_order_form.html', {'form': form, 'title': 'Редактировать заказ'})

@user_passes_test(is_admin)
def order_delete(request, order_id):
    # удалить заказ (админ)
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ удален!')
        return redirect('abibas:dashboard_order_list')
    return render(request, 'abibas/dashboard_order_confirm_delete.html', {'order': order})

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = '__all__'

@user_passes_test(is_admin)
def cart_list(request):
    # список корзин (админ)
    carts = Cart.objects.all()
    return render(request, 'abibas/dashboard_cart_list.html', {'carts': carts})

@user_passes_test(is_admin)
def cart_create(request):
    # создать корзину (админ)
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Корзина создана!')
            return redirect('abibas:dashboard_cart_list')
    else:
        form = CartForm()
    return render(request, 'abibas/dashboard_cart_form.html', {'form': form, 'title': 'Создать корзину'})

@user_passes_test(is_admin)
def cart_edit(request, cart_id):
    # редактировать корзину (админ)
    cart = Cart.objects.get(pk=cart_id)
    if request.method == 'POST':
        form = CartForm(request.POST, instance=cart)
        if form.is_valid():
            form.save()
            messages.success(request, 'Корзина обновлена!')
            return redirect('abibas:dashboard_cart_list')
    else:
        form = CartForm(instance=cart)
    return render(request, 'abibas/dashboard_cart_form.html', {'form': form, 'title': 'Редактировать корзину'})

@user_passes_test(is_admin)
def cart_delete(request, cart_id):
    # удалить корзину (админ)
    cart = Cart.objects.get(pk=cart_id)
    if request.method == 'POST':
        cart.delete()
        messages.success(request, 'Корзина удалена!')
        return redirect('abibas:dashboard_cart_list')
    return render(request, 'abibas/dashboard_cart_confirm_delete.html', {'cart': cart})

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'

@user_passes_test(is_admin)
def brand_list(request):
    # список брендов (админ)
    brands = Brand.objects.all()
    return render(request, 'abibas/dashboard_brand_list.html', {'brands': brands})

@user_passes_test(is_admin)
def brand_create(request):
    # создать бренд (админ)
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Бренд создан!')
            return redirect('abibas:dashboard_brand_list')
    else:
        form = BrandForm()
    return render(request, 'abibas/dashboard_brand_form.html', {'form': form, 'title': 'Создать бренд'})

@user_passes_test(is_admin)
def brand_edit(request, brand_id):
    # редактировать бренд (админ)
    brand = Brand.objects.get(pk=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Бренд обновлен!')
            return redirect('abibas:dashboard_brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'abibas/dashboard_brand_form.html', {'form': form, 'title': 'Редактировать бренд'})

@user_passes_test(is_admin)
def brand_delete(request, brand_id):
    # удалить бренд (админ)
    brand = Brand.objects.get(pk=brand_id)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Бренд удален!')
        return redirect('abibas:dashboard_brand_list')
    return render(request, 'abibas/dashboard_brand_confirm_delete.html', {'brand': brand})

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

@user_passes_test(is_admin)
def category_list(request):
    # список категорий (админ)
    categories = Category.objects.all()
    return render(request, 'abibas/dashboard_category_list.html', {'categories': categories})

@user_passes_test(is_admin)
def category_create(request):
    # создать категорию (админ)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория создана!')
            return redirect('abibas:dashboard_category_list')
    else:
        form = CategoryForm()
    return render(request, 'abibas/dashboard_category_form.html', {'form': form, 'title': 'Создать категорию'})

@user_passes_test(is_admin)
def category_edit(request, category_id):
    # редактировать категорию (админ)
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена!')
            return redirect('abibas:dashboard_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'abibas/dashboard_category_form.html', {'form': form, 'title': 'Редактировать категорию'})

@user_passes_test(is_admin)
def category_delete(request, category_id):
    # удалить категорию (админ)
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория удалена!')
        return redirect('abibas:dashboard_category_list')
    return render(request, 'abibas/dashboard_category_confirm_delete.html', {'category': category})

@user_passes_test(is_admin)
def userlog_list(request):
    # логи пользователей (админ)
    logs = UserLog.objects.select_related('user').order_by('-timestamp')[:200]
    return render(request, 'abibas/dashboard_userlog_list.html', {'logs': logs})

@user_passes_test(is_admin)
def backup_restore(request):
    # бэкап и восстановление БД (админ)
    message = None
    if request.method == 'POST' and request.FILES.get('backup_file'):
        backup_file = request.FILES['backup_file']
        db_path = settings.DATABASES['default']['NAME']
        with open(db_path, 'wb+') as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)
        message = 'База данных успешно восстановлена!'
    return render(request, 'abibas/dashboard_backup.html', {'message': message})

@user_passes_test(is_admin)
def download_backup(request):
    # скачать бэкап БД (админ)
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename='db_backup.sqlite3')
        return response
    return HttpResponseRedirect(reverse('abibas:backup_restore'))

def profile(request):
    # профиль пользователя
    user = request.user
    if user.role == 'seller':
        products = Product.objects.filter(seller=user)
    else:
        products = None
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'abibas/profile.html', {
        'user': user,
        'products': products,
        'orders': orders,
        'full_name': user.full_name,
        'total_orders': orders.count()
    })

@login_required
def profile_update(request):
    # редактирование профиля
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('abibas:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'abibas/profile_update.html', {
        'form': form,
        'title': 'Редактирование профиля'
    })

def is_seller(user):
    # проверка на продавца
    return user.role == 'seller'

def is_warehouse(user):
    # проверка на складовщика
    return user.role == 'warehouse'

@user_passes_test(is_seller)
def seller_dashboard(request):
    # панель продавца
    if not is_seller(request.user):
        return HttpResponseForbidden('Доступ запрещён')
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'abibas/seller_dashboard.html', {
        'products': products,
        'orders': orders
    })

@user_passes_test(is_seller)
def seller_product_list(request):
    # список товаров продавца
    products = Product.objects.all()
    return render(request, 'abibas/seller_product_list.html', {'products': products})

@user_passes_test(is_seller)
def seller_order_list(request):
    # список заказов продавца
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'abibas/seller_order_list.html', {'orders': orders})

@user_passes_test(is_warehouse)
def warehouse_product_list(request):
    # список товаров на складе
    products = Product.objects.all()
    return render(request, 'abibas/warehouse_product_list.html', {'products': products})

@user_passes_test(is_warehouse)
def warehouse_order_list(request):
    # список заказов на складе
    # Показываем все заказы, кроме доставленных и отмененных
    orders = Order.objects.exclude(status__in=['delivered', 'cancelled']).order_by('-created_at')
    return render(request, 'abibas/warehouse_order_list.html', {'orders': orders})

@user_passes_test(is_seller)
def seller_product_create(request):
    # создать товар (продавец)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Товар успешно добавлен')
            return redirect('abibas:seller_product_list')
    else:
        form = ProductForm()
    return render(request, 'abibas/seller_product_form.html', {
        'form': form,
        'title': 'Добавить товар'
    })

@user_passes_test(is_seller)
def seller_product_edit(request, product_id):
    # редактировать товар (продавец)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('abibas:seller_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'abibas/seller_product_form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product
    })

@user_passes_test(is_seller)
def seller_product_delete(request, product_id):
    # удалить товар (продавец)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален')
        return redirect('abibas:seller_product_list')
    return render(request, 'abibas/seller_product_confirm_delete.html', {
        'product': product
    })

@user_passes_test(is_seller)
def seller_order_detail(request, order_id):
    # детали заказа (продавец)
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'abibas/seller_order_detail.html', {
        'order': order
    })

@user_passes_test(is_seller)
def seller_order_status_update(request, order_id):
    # смена статуса заказа (продавец)
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлен')
        return redirect('abibas:seller_order_list')
    return render(request, 'abibas/seller_order_status_form.html', {
        'order': order
    })

@user_passes_test(is_warehouse)
def warehouse_product_update_stock(request, product_id):
    # изменение количества товара на складе
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 1))
        
        if action == 'add':
            product.stock += quantity
            messages.success(request, f'Добавлено {quantity} единиц товара')
        elif action == 'remove':
            if product.stock >= quantity:
                product.stock -= quantity
                messages.success(request, f'Списано {quantity} единиц товара')
            else:
                messages.error(request, 'Недостаточно товара на складе')
        
        product.save()
        return redirect('abibas:warehouse_product_list')
    
    return render(request, 'abibas/warehouse_product_stock_form.html', {
        'product': product
    })

@user_passes_test(is_warehouse)
def warehouse_order_process(request, order_id):
    # обработка заказа на складе
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            # Если меняем статус на "shipped", проверяем наличие товаров
            if new_status == 'shipped':
                can_ship = True
                for item in order.orderitem_set.all():
                    if item.product.stock < item.quantity:
                        can_ship = False
                        messages.error(request, f'Недостаточно товара {item.product.name} на складе')
                        break
                
                if can_ship:
                    # Списываем товары со склада
                    for item in order.orderitem_set.all():
                        item.product.stock -= item.quantity
                        item.product.save()
                    order.status = new_status
                    order.save()
                    messages.success(request, f'Заказ #{order.id} отправлен')
            else:
                order.status = new_status
                order.save()
                messages.success(request, f'Статус заказа #{order.id} обновлен на {order.get_status_display()}')
        
        return redirect('abibas:warehouse_dashboard')
    
    return render(request, 'abibas/warehouse_order_process_form.html', {
        'order': order
    })
