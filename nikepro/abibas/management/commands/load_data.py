from django.core.management.base import BaseCommand
from abibas.models import User, Brand, Category, Product
import os
from django.core.files import File
from django.conf import settings

class Command(BaseCommand):
    help = 'Loads test data into the database'

    def handle(self, *args, **kwargs):
        # Создаем суперпользователя
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Created superuser'))

        # Создаем бренды
        brands_data = [
            {'name': 'Nike', 'description': 'Just Do It'},
            {'name': 'Adidas', 'description': 'Impossible Is Nothing'},
            {'name': 'Puma', 'description': 'Forever Faster'},
            {'name': 'New Balance', 'description': 'Fearlessly Independent'},
            {'name': 'Reebok', 'description': 'Be More Human'},
        ]

        for brand_data in brands_data:
            Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data['description']}
            )
        self.stdout.write(self.style.SUCCESS('Created brands'))

        # Создаем категории
        categories_data = [
            {'name': 'Беговые', 'description': 'Кроссовки для бега'},
            {'name': 'Баскетбольные', 'description': 'Кроссовки для баскетбола'},
            {'name': 'Повседневные', 'description': 'Повседневные кроссовки'},
            {'name': 'Тренировочные', 'description': 'Кроссовки для тренировок'},
            {'name': 'Футбольные', 'description': 'Кроссовки для футбола'},
        ]

        for category_data in categories_data:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
        self.stdout.write(self.style.SUCCESS('Created categories'))

        # Создаем товары
        products_data = [
            {
                'name': 'Nike Air Max 270',
                'brand': 'Nike',
                'category': 'Повседневные',
                'description': 'Культовые кроссовки с технологией Air',
                'price': 12990,
                'size': '42',
                'color': 'Черный',
                'stock': 10,
            },
            {
                'name': 'Adidas Ultraboost 22',
                'brand': 'Adidas',
                'category': 'Беговые',
                'description': 'Инновационные беговые кроссовки',
                'price': 15990,
                'size': '43',
                'color': 'Белый',
                'stock': 15,
            },
            {
                'name': 'Puma RS-X',
                'brand': 'Puma',
                'category': 'Повседневные',
                'description': 'Ретро-стиль с современными технологиями',
                'price': 11990,
                'size': '41',
                'color': 'Серый',
                'stock': 8,
            },
            {
                'name': 'New Balance 574',
                'brand': 'New Balance',
                'category': 'Повседневные',
                'description': 'Классические кроссовки для повседневной носки',
                'price': 9990,
                'size': '44',
                'color': 'Синий',
                'stock': 12,
            },
            {
                'name': 'Reebok Classic Leather',
                'brand': 'Reebok',
                'category': 'Повседневные',
                'description': 'Классические кожаные кроссовки',
                'price': 8990,
                'size': '42',
                'color': 'Белый',
                'stock': 20,
            },
            {
                'name': 'Nike Air Jordan 1',
                'brand': 'Nike',
                'category': 'Баскетбольные',
                'description': 'Легендарные баскетбольные кроссовки',
                'price': 18990,
                'size': '43',
                'color': 'Красный',
                'stock': 5,
            },
            {
                'name': 'Adidas Predator Edge',
                'brand': 'Adidas',
                'category': 'Футбольные',
                'description': 'Профессиональные футбольные бутсы',
                'price': 14990,
                'size': '42',
                'color': 'Черный',
                'stock': 7,
            },
            {
                'name': 'Puma Future Z',
                'brand': 'Puma',
                'category': 'Футбольные',
                'description': 'Инновационные футбольные бутсы',
                'price': 13990,
                'size': '41',
                'color': 'Белый',
                'stock': 9,
            },
            {
                'name': 'New Balance Fresh Foam X',
                'brand': 'New Balance',
                'category': 'Беговые',
                'description': 'Комфортные беговые кроссовки',
                'price': 12990,
                'size': '44',
                'color': 'Серый',
                'stock': 11,
            },
            {
                'name': 'Reebok Nano X1',
                'brand': 'Reebok',
                'category': 'Тренировочные',
                'description': 'Кроссовки для кроссфита',
                'price': 11990,
                'size': '43',
                'color': 'Черный',
                'stock': 14,
            },
        ]

        # Создаем директорию для изображений, если её нет
        media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_dir, exist_ok=True)

        for product_data in products_data:
            brand = Brand.objects.get(name=product_data['brand'])
            category = Category.objects.get(name=product_data['category'])
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'brand': brand,
                    'category': category,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'size': product_data['size'],
                    'color': product_data['color'],
                    'stock': product_data['stock'],
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded test data')) 