from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from abibas.models import Brand, Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Загружает начальные данные в базу данных'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Создаем администратора, если его нет
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь admin'))

        # Создаем бренды
        brands_data = [
            {'name': 'Nike', 'description': 'Американский производитель спортивной одежды и обуви'},
            {'name': 'Adidas', 'description': 'Немецкий производитель спортивной одежды и обуви'},
            {'name': 'Puma', 'description': 'Немецкий производитель спортивной одежды, обуви и аксессуаров'},
            {'name': 'Reebok', 'description': 'Производитель спортивной одежды и обуви'},
            {'name': 'New Balance', 'description': 'Американский производитель спортивной одежды и обуви'}
        ]

        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(**brand_data)
            brands[brand.name] = brand
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан бренд {brand.name}'))

        # Создаем категории
        categories_data = [
            {'name': 'Кроссовки для бега', 'description': 'Обувь для бега и тренировок'},
            {'name': 'Повседневные кроссовки', 'description': 'Обувь для повседневной носки'},
            {'name': 'Баскетбольные кроссовки', 'description': 'Обувь для баскетбола'},
            {'name': 'Футбольная обувь', 'description': 'Обувь для футбола'},
            {'name': 'Кроссовки для тренировок', 'description': 'Обувь для тренажерного зала'}
        ]

        categories = {}
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(**category_data)
            categories[category.name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория {category.name}'))

        # Создаем товары
        products_data = [
            {
                'name': 'Nike Air Max 270',
                'brand': brands['Nike'],
                'category': categories['Повседневные кроссовки'],
                'description': 'Стильные и комфортные кроссовки для повседневной носки',
                'price': Decimal('12999.99'),
                'size': '40-45',
                'color': 'Черный/Белый',
                'stock': 50
            },
            {
                'name': 'Adidas Ultraboost',
                'brand': brands['Adidas'],
                'category': categories['Кроссовки для бега'],
                'description': 'Профессиональные беговые кроссовки с технологией Boost',
                'price': Decimal('14999.99'),
                'size': '39-46',
                'color': 'Синий',
                'stock': 30
            },
            {
                'name': 'Puma RS-X',
                'brand': brands['Puma'],
                'category': categories['Повседневные кроссовки'],
                'description': 'Модные кроссовки в стиле ретро',
                'price': Decimal('8999.99'),
                'size': '38-45',
                'color': 'Белый/Красный',
                'stock': 40
            },
            {
                'name': 'Reebok Nano X',
                'brand': brands['Reebok'],
                'category': categories['Кроссовки для тренировок'],
                'description': 'Кроссовки для кроссфита и тренировок',
                'price': Decimal('10999.99'),
                'size': '40-46',
                'color': 'Черный',
                'stock': 25
            },
            {
                'name': 'New Balance 574',
                'brand': brands['New Balance'],
                'category': categories['Повседневные кроссовки'],
                'description': 'Классические кроссовки для повседневной носки',
                'price': Decimal('9999.99'),
                'size': '39-45',
                'color': 'Серый',
                'stock': 35
            },
            {
                'name': 'Nike Zoom Lebron',
                'brand': brands['Nike'],
                'category': categories['Баскетбольные кроссовки'],
                'description': 'Профессиональные баскетбольные кроссовки',
                'price': Decimal('15999.99'),
                'size': '41-47',
                'color': 'Черный/Золотой',
                'stock': 20
            },
            {
                'name': 'Adidas Predator',
                'brand': brands['Adidas'],
                'category': categories['Футбольная обувь'],
                'description': 'Профессиональные футбольные бутсы',
                'price': Decimal('13999.99'),
                'size': '40-45',
                'color': 'Красный/Черный',
                'stock': 30
            },
            {
                'name': 'Puma Future Z',
                'brand': brands['Puma'],
                'category': categories['Футбольная обувь'],
                'description': 'Легкие и маневренные футбольные бутсы',
                'price': Decimal('11999.99'),
                'size': '39-44',
                'color': 'Желтый/Черный',
                'stock': 25
            }
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан товар {product.name}'))

        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена успешно!')) 