from unicodedata import category
from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаление всех статей в выбранной категории'
    # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)
    requires_migrations_checks = True

    def handle(self, *args, **options):
        cat = 'education'
        # здесь можете писать любой код, который выполнется при вызове вашей команды
        self.stdout.write(f'Удалить все статьи в категории {cat}? y/n')
        answer = input()
        if answer == 'y':
            Post.objects.all().filter(category=Category.objects.get(categoryName=cat)).delete()
            self.stdout.write('Удаление выполнено')
            return
        self.stdout.write(self.style.ERROR('Access denied'))
