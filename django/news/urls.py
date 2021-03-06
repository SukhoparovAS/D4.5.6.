from unicodedata import category
from django.urls import path, include
from .views import AuthorList, PostList, PostDetail, PostCreateView, PostUpdateView, PostDeleteView, subscribe, Post_by_category

urlpatterns = [
    path('', PostList.as_view()),
    path('authors/', AuthorList.as_view()),
    path('post/<int:pk>', PostDetail.as_view()),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('post_delete/<int:pk>', PostDeleteView.as_view()),
    path('post_update/<int:pk>', PostUpdateView.as_view()),
    path('subscribe/<int:pk>', subscribe),
    path('category/<int:pk>', Post_by_category.as_view())
]
