import re

from apps.accounts.models import Profile
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Post, Tag, Feed, Follow

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_feed_selffollow(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Feed.objects.create(user=instance)
        Follow.objects.create(followed=instance, follower=instance)


@receiver(post_save, sender=Post)
def parse_and_create_post_tags(sender, instance, created, **kwargs):
    if created:
        post = instance
        tags_list = [tag.strip('#') for tag in re.findall(r'#\w+', post.text)]
        if tags_list:
            tags_objs = [Tag.objects.get_or_create(title=tag)[0] for tag in tags_list]
            post.tags.set(tags_objs)
            post.text = post.text.split('#')[0]
            post.save_without_signals()


@receiver(post_save, sender=Post)
def add_post_into_followers_feed(sender, instance, created, **kwargs):
    if created:
        post = instance
        follows = Follow.objects.filter(followed=post.user)
        for follow in follows:
            follower_feed = follow.follower.feed
            follower_feed.posts.add(post)
            follower_feed.save()


@receiver(post_save, sender=Follow)
def add_followed_user_to_follower_feed(sender, instance, created, **kwargs):
    if created:
        follower = instance.follower
        followed = instance.followed
        follower.feed.posts.add(*followed.posts.all())


@receiver(post_delete, sender=Follow)
def remove_followed_user_from_follower_feed(sender, instance, **kwargs):
    follower = instance.follower
    followed = instance.followed
    if Feed.objects.filter(user=follower).exists():
        follower.feed.posts.remove(*followed.posts.all())
