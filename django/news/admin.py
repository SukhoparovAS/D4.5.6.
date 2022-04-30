from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, BanWords, Subscriber


class PostAdmin(admin.ModelAdmin):

    list_display = ('title', 'author')


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(BanWords)
admin.site.register(Subscriber)
