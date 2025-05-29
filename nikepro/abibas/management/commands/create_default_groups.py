from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создает стандартные группы пользователей, если они еще не существуют'

    def handle(self, *args, **options):
        group_name = 'Покупатель'
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" успешно создана.'))
        else:
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует.')) 