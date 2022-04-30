from django.forms import ModelForm
from .models import Post, Author
from django.contrib.auth.models import User


# Создаём модельную форму
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category']
