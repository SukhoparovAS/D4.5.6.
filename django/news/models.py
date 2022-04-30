from tkinter import CASCADE
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.cache import cache


# Модель, содержащая объекты всех авторов


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postrating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postrating')

        commentRat = self.user.comment_set.all().aggregate(
            commentrating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentrating')

        self.rating = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return f'{self.user.username.title()}'

# Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.)


class Category(models.Model):
    categoryName = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.categoryName.title()}'

# Эта модель должна содержать в себе статьи и новости, которые создают пользователи.


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )

    type = models.CharField(
        max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    creationDate = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255, default='Нет заголовка')
    text = models.TextField(default='Нет текста статьи')
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.title.title()}'

    def preview(self):
        return self.text[0:123] + '...'

    # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
    def get_absolute_url(self):
        return f'/post/{self.id}'

    def save(self, *args, **kwargs):
        # сначала вызываем метод родителя, чтобы объект сохранился
        super().save(*args, **kwargs)
        # затем удаляем его из кэша, чтобы сбросить его
        cache.delete(f'post-{self.pk}')

# Промежуточная модель для связи «многие ко многим»:


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pk}:{self.post.title.title()} ({self.category.categoryName.title()})'

# Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать их способ хранения тоже.


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default='Нет текста комментария')
    creationDate = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return f'{self.post.title.title()} ({self.text.title()})'


class BanWords(models.Model):
    wordsList = models.TextField()


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self) -> str:
        return f'{self.user.username.title()} ({self.category.categoryName.title()})'
