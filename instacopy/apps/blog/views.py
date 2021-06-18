import json
import random
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DetailView, CreateView

from .forms import PostCreationForm
from .models import Post, Feed, Follow, Tag, Like, Saved
from .services import add_like, remove_like, add_saved, remove_saved, follow_user, unfollow_user, is_followed

User = get_user_model()


class FeedView(LoginRequiredMixin, ListView):
    template_name = 'blog/feed.html'
    login_url = reverse_lazy('account_login')

    def get_queryset(self):
        feed = Feed.objects.prefetch_related(
            Prefetch('posts', queryset=(Post.objects
                                        .select_related('user__profile')
                                        .prefetch_related('likes', 'tags')))
        ).get(user=self.request.user)
        self.post_list = feed.posts.all()
        return self.post_list

    def get_context_object_name(self, object_list):
        return 'post_list'

    def get_context_data(self, *args, **kwargs):
        context = super(FeedView, self).get_context_data(*args, **kwargs)

        user = self.request.user
        context['from_feed'] = True

        context['liked_by_user'] = self._liked_by_user(user=user, posts=self.post_list)
        context['saved_by_user'] = self._saved_by_user(user=user, posts=self.post_list)

        context['suggested_users'] = User.objects.filter(
            username__in=['userone', 'usertwo', 'userthree', 'userfour', 'userfive']
        ).exclude(username=user.username).select_related('profile')
        context['followed_by_user'] = self._followed_by_user(user=user)
        return context

    def _followed_by_user(self, user):
        followed_by_user = Follow.objects.filter(
            follower=user).values_list('followed__id', flat=True)
        return followed_by_user

    def _liked_by_user(self, user, posts):
        liked_by_user = Like.objects.filter(
            post__id__in=posts.values_list('id', flat=True)
        ).values_list('post__id', flat=True)
        return liked_by_user

    def _saved_by_user(self, user, posts):
        saved_by_user = Saved.objects.filter(
            post__id__in=posts.values_list('id', flat=True)
        ).values_list('post__id', flat=True)
        return saved_by_user


class BlogView(ListView):
    template_name = 'blog/blog.html'

    def get_queryset(self):
        self.blog_user = get_object_or_404(User, username=self.kwargs['username'])
        queryset = Post.objects.filter(user=self.blog_user)
        return queryset

    def get_context_object_name(self, object_list):
        return 'post_list'

    def get_context_data(self, *args, **kwargs):
        context = super(BlogView, self).get_context_data(*args, **kwargs)
        context['blog_user'] = self.blog_user

        user = self.request.user
        if user.is_authenticated:
            context['current_user_page'] = (
                True if (self.blog_user == self.request.user) else False
            )
            if not context['current_user_page']:
                context['is_followed'] = is_followed(
                    followed=self.blog_user, follower=self.request.user
                )

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    login_url = reverse_lazy('account_login')
    form_class = PostCreationForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            media = form.cleaned_data.get('media')
            text = form.cleaned_data.get('text')

            tags_list = [tag.strip('#') for tag in re.findall(r'#\w+', text)]
            tags_objs = [Tag.objects.get_or_create(title=tag)[0] for tag in tags_list]
            text = text.split('#')[0]

            post, _ = Post.objects.get_or_create(user=request.user, media=media, text=text)
            post.tags.set(tags_objs)
            post.save()
            return HttpResponseRedirect('/')
        return render(request, self.template_name, {'form': form})


class PostDetailView(DetailView):
    template_name = 'blog/post_detail.html'
    slug_field = 'url'

    def get_object(self):
        self.object = (Post.objects
                       .select_related('user__profile')
                       .prefetch_related('likes', 'tags')
                       .get(url=self.kwargs.get('slug')))
        return self.object

    def get_context_object_name(self, obj):
        return 'post'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)
        context['liked_by_user'] = self._liked_by_user(
            user=self.request.user, post=self.object)
        context['saved_by_user'] = self._saved_by_user(
            user=self.request.user, post=self.object)
        return context

    def _liked_by_user(self, user, post):
        liked_by_user = ((post.id,)
                         if Like.objects.filter(post__id=post.id).exists()
                         else ())
        return liked_by_user

    def _saved_by_user(self, user, post):
        saved_by_user = ((post.id,)
                         if Saved.objects.filter(post__id=post.id).exists()
                         else ())
        return saved_by_user


class TagDetailView(DetailView):
    model = Tag
    template_name = 'blog/tag_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TagDetailView, self).get_context_data(*args, **kwargs)

        posts = self.object.posts.all()
        context['post_list'] = posts

        random_tag_photo_url = random.choice(posts).media.url
        context['random_tag_photo_url'] = random_tag_photo_url
        return context

    def get_context_object_name(self, obj):
        return 'tag'


class SavedToggleView(View):
    def post(self, request, slug):
        if self.request.is_ajax():
            data = json.loads(request.POST['json_data'])
            is_saved = data.get("is_saved")

            user = request.user
            post = Post.objects.get(url=slug)

            response = {}
            if user.is_authenticated:
                if is_saved:
                    remove_saved(post=post, user=user)
                    response['is_saved'] = False
                else:
                    add_saved(post=post, user=user)
                    response['is_saved'] = True
                return JsonResponse(response, status=200)
            else:
                response['message'] = 'Authorization required'
                return JsonResponse(response, status=403)


class LikeToggleView(View):
    def post(self, request, slug):
        if self.request.is_ajax():
            data = json.loads(request.POST['json_data'])
            object_content_type = data.get("object_content_type")
            is_liked = data.get("is_liked")
            user = request.user
            if object_content_type == 'post':
                obj = Post.objects.get(url=slug)
            response = {}
            if user.is_authenticated:
                if is_liked:
                    remove_like(obj=obj, user=user)
                    response['is_liked'] = False
                else:
                    add_like(obj=obj, user=user)
                    response['is_liked'] = True
                return JsonResponse(response, status=200)
            else:
                response['message'] = 'Authorization required'
                return JsonResponse(response, status=403)


class FollowToggle(View):
    def post(self, request, username):
        if self.request.is_ajax():
            data = json.loads(request.POST['json_data'])
            followed_id = data.get("followed_id")
            is_followed = data.get("is_followed")

            followed = User.objects.get(id=followed_id)
            follower = request.user

            response = {}
            if request.user.is_authenticated:
                if is_followed:
                    unfollow_user(followed=followed, follower=follower)
                    response['is_followed'] = False
                else:
                    follow_user(followed=followed, follower=follower)
                    response['is_followed'] = True
                return JsonResponse(response, status=200)
            else:
                response['message'] = 'Authorization required'
                return JsonResponse(response, status=403)
