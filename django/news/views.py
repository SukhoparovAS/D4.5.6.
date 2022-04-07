from gettext import Catalog
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, CreateView, DetailView, UpdateView
from .models import Author, Category, Post
from django.shortcuts import render
from django.views import View  # импортируем простую вьюшку
# импортируем класс, позволяющий удобно осуществлять постраничный вывод
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class AuthorList(ListView):
    model = Author
    template_name = 'authors.html'
    context_object_name = 'authors'


class PostList(LoginRequiredMixin, ListView):
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
        context['is_not_premium'] = not self.request.user.groups.filter(
            name='authors').exists()
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post', )


class PostDetail(DeleteView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


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
