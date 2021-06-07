from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import Follow, Like, Saved

User = get_user_model()


def add_like(obj, user):
    """Лайкает `obj`.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    like, is_created = Like.objects.get_or_create(
        content_type=obj_type, object_id=obj.id, user=user)
    return like


def remove_like(obj, user):
    """Удаляет лайк с `obj`.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    Like.objects.filter(
        content_type=obj_type, object_id=obj.id, user=user
    ).delete()


def add_saved(post, user):
    """Добавляет `post` в сохраненное.
    """
    saved, is_created = Saved.objects.get_or_create(post=post, user=user)
    return saved


def remove_saved(post, user):
    """Удаляет `post` из сохраненного.
    """
    Saved.objects.filter(post=post, user=user).delete()


def follow_user(followed, follower):
    follow, is_created = Follow.objects.get_or_create(
        followed=followed, follower=follower)
    return follow


def unfollow_user(followed, follower):
    Follow.objects.filter(followed=followed, follower=follower).delete()


def is_followed(followed, follower):
    return Follow.objects.filter(followed=followed, follower=follower).exists()
