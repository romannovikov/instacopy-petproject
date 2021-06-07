import random

from apps.accounts.models import Profile
from apps.blog.models import Post, Tag
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

User = get_user_model()

usernames = ['userone', 'usertwo', 'userthree', 'userfour', 'userfive']

users_data = [{"username": username,
               "email": username + "@test.com",
               "full_name": 'User ' + username[4:].capitalize(),
               "password": make_password("badpassword")}
              for username in usernames]

all_tags = [f'#tag{i}' for i in range(18)]

posts_data = []
for username in usernames:
    for i in range(24):
        choices_tags = ", ".join(random.sample(all_tags, 3))
        post_data = {"username": username,
                     "media": f"users/{username}/posts/{i}.jpg",
                     "text": f"default post text with tags {choices_tags}"}
        posts_data.append(post_data)


class Command(BaseCommand):
    help = 'Create initial objects in db'

    def handle(self, *args, **options):
        User.objects.exclude(username='superuser').delete()
        Tag.objects.all().delete()

        self.stdout.write(self.style.WARNING('Starting the process.'))
        self.stdout.write(self.style.WARNING('Creating initial users...'))

        users = [User(**user_data) for user_data in users_data]
        for user in users:
            user.save()
            (Profile.objects
             .filter(user=user)
             .update(photo=f"users/{user.username}/profile/0.jpg"))

        self.stdout.write(self.style.SUCCESS('Initial users have been created.'))
        self.stdout.write(self.style.WARNING("Creating user posts..."))

        while posts_data:
            random_post_data = random.choice(posts_data)
            user = User.objects.get(username=random_post_data['username'])
            post_obj = Post(user=user,
                            media=random_post_data['media'],
                            text=random_post_data['text'])
            post_obj.save()
            posts_data.remove(random_post_data)

            if bool(posts_data) & (len(posts_data) % 10 == 0):
                self.stdout.write(self.style.WARNING(f"{len(posts_data)} posts left..."))

        self.stdout.write(self.style.SUCCESS('All initial objects have been created.'))
