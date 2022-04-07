from .models import Post
import django_filters
from django_filters import FilterSet, DateFilter, CharFilter
from .models import Author, Post

# создаём фильтр


class PostFilter(FilterSet):
    datetime__lte = DateFilter(field_name='creationDate',
                               input_formats=[
                                   '%Y-%m-%d', '%d-%m-%Y', '%Y.%m.%d', '%d.%m.%Y'],
                               lookup_expr='gt',
                               label=('Date'),

                               )
    title__icontains = CharFilter(field_name='title',
                                  lookup_expr='icontains',
                                  label=('Title'),
                                  )
    all_posts = Author.objects.all()
    all_authors = ()
    for i in all_posts:
        new = (str(i.id), str(i.user.username))
        all_authors += (new,)
    all_authors += (('', 'ALL'),)

    author__in = django_filters.ChoiceFilter(
        field_name='author', lookup_expr='in', choices=all_authors)

    class Meta:
        model = Post
        fields = {
            # 'author': ['in'],
            # 'title': ['icontains'],
            # 'creationDate': ['gt'],
        }
