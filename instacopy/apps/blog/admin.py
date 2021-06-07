from django.contrib import admin

from .models import Feed, Follow, Post, Tag, Like, Saved

admin.site.register([Feed, Follow, Post, Tag, Like, Saved])
