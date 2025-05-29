from django.urls import path
from . import views

app_name = 'abibas'

# ---------------------------------------------
# Маршруты приложения abibas
# Описывает все URL для пользовательской, складской, продавецкой и админской частей
# ---------------------------------------------

urlpatterns = [
    # --- Пользовательские маршруты ---
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),

    # --- Админские маршруты ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/users/', views.user_list, name='dashboard_user_list'),
    path('dashboard/users/create/', views.user_create, name='dashboard_user_create'),
    path('dashboard/users/<int:user_id>/edit/', views.user_edit, name='dashboard_user_edit'),
    path('dashboard/users/<int:user_id>/delete/', views.user_delete, name='dashboard_user_delete'),
    path('dashboard/products/', views.admin_product_list, name='dashboard_product_list'),
    path('dashboard/products/create/', views.product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:product_id>/edit/', views.product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:product_id>/delete/', views.product_delete, name='dashboard_product_delete'),
    path('dashboard/orders/', views.admin_order_list, name='dashboard_order_list'),
    path('dashboard/orders/create/', views.order_create, name='dashboard_order_create'),
    path('dashboard/orders/<int:order_id>/edit/', views.order_edit, name='dashboard_order_edit'),
    path('dashboard/orders/<int:order_id>/delete/', views.order_delete, name='dashboard_order_delete'),
    path('dashboard/carts/', views.cart_list, name='dashboard_cart_list'),
    path('dashboard/carts/create/', views.cart_create, name='dashboard_cart_create'),
    path('dashboard/carts/<int:cart_id>/edit/', views.cart_edit, name='dashboard_cart_edit'),
    path('dashboard/carts/<int:cart_id>/delete/', views.cart_delete, name='dashboard_cart_delete'),
    path('dashboard/brands/', views.brand_list, name='dashboard_brand_list'),
    path('dashboard/brands/create/', views.brand_create, name='dashboard_brand_create'),
    path('dashboard/brands/<int:brand_id>/edit/', views.brand_edit, name='dashboard_brand_edit'),
    path('dashboard/brands/<int:brand_id>/delete/', views.brand_delete, name='dashboard_brand_delete'),
    path('dashboard/categories/', views.category_list, name='dashboard_category_list'),
    path('dashboard/categories/create/', views.category_create, name='dashboard_category_create'),
    path('dashboard/categories/<int:category_id>/edit/', views.category_edit, name='dashboard_category_edit'),
    path('dashboard/categories/<int:category_id>/delete/', views.category_delete, name='dashboard_category_delete'),
    path('dashboard/userlogs/', views.userlog_list, name='dashboard_userlog_list'),
    path('dashboard/backup/', views.backup_restore, name='backup_restore'),
    path('dashboard/backup/download/', views.download_backup, name='download_backup'),

    # --- Продавец ---
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/', views.seller_product_list, name='seller_product_list'),
    path('seller/products/create/', views.seller_product_create, name='seller_product_create'),
    path('seller/products/<int:product_id>/edit/', views.seller_product_edit, name='seller_product_edit'),
    path('seller/products/<int:product_id>/delete/', views.seller_product_delete, name='seller_product_delete'),
    path('seller/orders/', views.seller_order_list, name='seller_order_list'),
    path('seller/orders/<int:order_id>/', views.seller_order_detail, name='seller_order_detail'),

    # --- Склад ---
    path('warehouse/', views.warehouse_order_list, name='warehouse_dashboard'),
    path('warehouse/products/', views.warehouse_product_list, name='warehouse_product_list'),
    path('warehouse/products/<int:product_id>/stock/', views.warehouse_product_update_stock, name='warehouse_product_update_stock'),
    path('warehouse/orders/', views.warehouse_order_list, name='warehouse_order_list'),
    path('warehouse/orders/<int:order_id>/process/', views.warehouse_order_process, name='warehouse_order_process'),
] 