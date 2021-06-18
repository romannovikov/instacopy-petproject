import hashlib
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unixtimestampfield.fields import UnixTimeStampField

# from image_cropping import ImageRatioField

User = get_user_model()


def user_media_directory(instance, filename):
    return f'users/{instance.user}/posts/{filename}'  # ???


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media = models.ImageField(upload_to=user_media_directory, verbose_name='Media')
    text = models.TextField(max_length=1024, verbose_name='Text', null=True, blank=True)
    url = models.SlugField(max_length=32, unique=True)
    created_at = UnixTimeStampField(auto_now_add=True)

    # relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    likes = GenericRelation('Like', related_query_name='post')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} | {self.id}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.url])

    def get_save_url(self):
        return reverse('save_toggle', args=[self.url])

    def get_like_url(self):
        return reverse('like_toggle', args=[self.url])

    @property
    def total_likes(self):
        return self.likes.count()

    def save_without_signals(self):
        """
        Взято из https://stackoverflow.com/questions/10840030/django-post-save-preventing-recursion-without-overriding-model-save
        This allows for updating the model from code running inside post_save()
        signals without going into an infinite loop:
        """
        self._disable_signals = True
        self.save()
        self._disable_signals = False

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = hashlib.md5(f'{self.id}'.encode('utf-8')).hexdigest()
        return super().save(*args, **kwargs)


class Tag(models.Model):
    title = models.CharField(max_length=16, verbose_name='Tag')
    slug = models.SlugField(unique=True)
    created_at = UnixTimeStampField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.title}'

    def get_absolute_url(self):
        return reverse('tag_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Feed(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    posts = models.ManyToManyField(settings.POST_MODEL, blank=True, related_name='posts')

    def __str__(self):
        return f'@{self.user.username} Feed object'  # ???


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_is_follower'
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_is_followed'
    )
    created_at = UnixTimeStampField(auto_now_add=True)

    def __str__(self):
        return f'@{self.follower} is following @{self.followed}'


class Like(models.Model):
    user = models.ForeignKey(User,
                             related_name='likes',
                             on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = UnixTimeStampField(auto_now_add=True)

    def __str__(self):
        return f'{self.content_type} with id {self.object_id} liked by {self.user}'  # ???


class Saved(models.Model):
    user = models.ForeignKey(User,
                             related_name='saved',
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE)
    created_at = UnixTimeStampField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Saved'

    def __str__(self):
        return f'{self.post} saved by {self.user}'  # ???
