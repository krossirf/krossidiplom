from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# ---------------------------------------------
# Модели приложения abibas
# Описывают структуру данных: пользователи, товары, заказы, корзины и т.д.
# ---------------------------------------------

# Модель пользователя (расширяет стандартную модель Django)
class User(AbstractUser):
    # Роль пользователя: обычный, продавец, складовщик, админ
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('seller', 'Продавец'),
        ('warehouse', 'Складовщик'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')  # Роль
    phone = models.CharField(max_length=20, blank=True, null=True)  # Телефон
    address = models.TextField(blank=True, null=True)  # Адрес
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Аватар

    @property
    def full_name(self):
        # Возвращает полное имя пользователя
        return f"{self.first_name} {self.last_name}".strip() or self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

# Модель бренда (например, Nike, Adidas)
class Brand(models.Model):
    name = models.CharField(max_length=100)  # Название бренда
    description = models.TextField(blank=True)  # Описание бренда
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

# Модель категории товара (например, Кроссовки, Одежда)
class Category(models.Model):
    name = models.CharField(max_length=100)  # Название категории
    description = models.TextField(blank=True)  # Описание категории
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

# Модель товара (кроссовки, одежда и т.д.)
class Product(models.Model):
    name = models.CharField(max_length=200)  # Название товара
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)  # Бренд
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Категория
    description = models.TextField()  # Описание
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])  # Цена
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])  # Количество на складе
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Добавляем поле для размеров
    SIZES = [
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('46', '46'),
        ('47', '47'),
        ('48', '48'),
    ]
    size = models.CharField(max_length=2, choices=SIZES, default='42')
    
    def __str__(self):
        return f"{self.brand.name} {self.name} - {self.size}"
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

# Модель корзины пользователя
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Владелец корзины
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления
    
    def __str__(self):
        return f"Корзина пользователя {self.user.username}"
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

# Модель товара в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Корзина
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Товар
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])  # Количество
    size = models.CharField(max_length=2, choices=Product.SIZES, default='42')  # Размер
    
    def __str__(self):
        return f"{self.product.name} (размер {self.size}) x {self.quantity}"
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'product', 'size']  # Уникальная комбинация корзины, товара и размера

# Модель заказа
class Order(models.Model):
    # Возможные статусы заказа
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Покупатель
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Статус заказа
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сумма заказа
    shipping_address = models.TextField()  # Адрес доставки
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

# Модель товара в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Заказ
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Товар
    quantity = models.IntegerField(default=1)  # Количество
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена за единицу
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

# Модель логов пользователя (например, вход, регистрация, оформление заказа)
class UserLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Вход'),
        ('register', 'Регистрация'),
        ('order', 'Оформление заказа'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Пользователь
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)  # Действие
    timestamp = models.DateTimeField(auto_now_add=True)  # Время действия
    info = models.TextField(blank=True)  # Доп. информация

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"
