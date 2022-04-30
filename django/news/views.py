from asyncio.windows_events import NULL
from gettext import Catalog
from unicodedata import category
from webbrowser import get
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, CreateView, DetailView, UpdateView
from requests import request
from urllib3 import HTTPResponse
from .models import Author, Category, Post, PostCategory, Subscriber
from django.shortcuts import render
from django.views import View  # импортируем простую вьюшку
# импортируем класс, позволяющий удобно осуществлять постраничный вывод
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.core.cache import cache  # импортируем наш кэш


class AuthorList(ListView):
    model = Author
    template_name = 'authors.html'
    context_object_name = 'authors'


class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-creationDate')
    paginate_by = 4
    form_class = PostForm
    # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post', )

    def form_valid(self, form):
        # создаем форму, но не отправляем его в БД, пока просто держим в памяти
        fields = form.save(commit=False)
        # Через реквест передаем недостающую форму, которая обязательна

        if Author.objects.all().filter(
                user=self.request.user).exists():
            fields.author = Author.objects.get(user=self.request.user)
        else:
            author = Author(user=self.request.user)
            author.save()
            fields.author = Author.objects.get(user=self.request.user)

        # Наконец сохраняем в БД
        fields.save()
        return super().form_valid(form)


class PostDetail(DeleteView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    # переопределяем метод получения объекта, как ни странно
    def get_object(self, *args, **kwargs):
        # кэш очень похож на словарь, и метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.
        obj = cache.get(f'product-{self.kwargs["pk"]}', None)

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj


def subscribe(request, pk):
    sub = Subscriber(user=request.user,
                     category=Category.objects.get(pk=pk))
    sub.save()
    return redirect(f'/category/{pk}')


class PostUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    ontext_object_name = 'post_update'
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.change_post', )

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/'
    permission_required = ('news.delete_post',)


class Post_by_category(ListView):
    model = Post
    template_name = 'post_by_category.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.all().filter(category=Category.objects.get(pk=self.kwargs['pk']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_subscribe'] = Subscriber.objects.all().filter(
                user=self.request.user).exists() and Subscriber.objects.all().filter(category=Category.objects.get(pk=self.kwargs.get('pk')))
        else:
            context['is_subscribe'] = True
        context['id'] = self.kwargs['pk']
        return context
