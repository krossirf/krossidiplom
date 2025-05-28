from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import path
from .models import Brand, Category, Product, Cart, CartItem, Order, OrderItem, User, UserLog

# ---------------------------------------------
# Админка приложения abibas
# Кастомизация интерфейса Django admin для моделей проекта
# ---------------------------------------------

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    list_per_page = 20

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['role'].disabled = True
        return form

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        
        # Базовые поля для всех
        fieldsets = [
            ('Основная информация', {
                'fields': ('username', 'password')
            }),
            ('Персональная информация', {
                'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'avatar')
            }),
        ]
        
        # Только суперпользователь может менять роль
        if request.user.is_superuser:
            fieldsets.append(
                ('Роль и статус', {
                    'fields': ('role', 'is_active')
                })
            )
        else:
            fieldsets.append(
                ('Статус', {
                    'fields': ('is_active',)
                })
            )
        
        return fieldsets

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email', 'first_name', 'last_name', 'phone', 'address', 'avatar', 'is_active'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return request.user.is_superuser or request.user == obj

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        if obj.role in ['seller', 'warehouse']:
            obj.is_staff = True
            obj.save()
        return response

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if obj.role in ['seller', 'warehouse']:
            obj.is_staff = True
            obj.save()
        return response

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role == 'seller'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'seller'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role == 'seller'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'seller'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'description')
    list_per_page = 20

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role == 'seller'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'seller'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'shipping_address')
    list_per_page = 20

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role == 'seller'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'seller'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product')
    search_fields = ('order__user__username', 'product__name')
    list_per_page = 20

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    list_per_page = 20

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    list_filter = ('cart', 'product')
    search_fields = ('cart__user__username', 'product__name')
    list_per_page = 20

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['seller', 'warehouse']

@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'info')
    readonly_fields = ('user', 'action', 'timestamp', 'info')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.site_header = 'Панель управления Abibas'
admin.site.site_title = 'Abibas Admin'
admin.site.index_title = 'Управление магазином'

# Отключаем стандартную модель Group
admin.site.unregister(Group)
