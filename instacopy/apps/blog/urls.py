from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    url(r'^(?P<username>\w+)/$', views.BlogView.as_view(), name='blog_page'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('p/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/like', views.LikeToggleView.as_view(), name='like_toggle'),
    path('<slug:slug>/save', views.SavedToggleView.as_view(), name='save_toggle'),
    url(r'^(?P<username>\w+)/follow$', views.FollowToggle.as_view(), name='follow_toggle'),
    path('explore/tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
]
