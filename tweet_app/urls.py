from django.urls import path
from tweet_app import views

urlpatterns = [
    path('', views.posts, name="posts"),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
]