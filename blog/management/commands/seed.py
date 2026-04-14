import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile, Channel, Post, ChannelFollow


class Command(BaseCommand):
    help = 'Seeds the database with users, channels, and posts'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--channels', type=int, default=100, help='Number of channels to create')
        parser.add_argument('--posts', type=int, default=200, help='Number of posts to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        num_users = options['users']
        num_channels = options['channels']
        num_posts = options['posts']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(username__startswith='user_').delete()

        self.stdout.write('Starting database seeding...')

        # Create users
        self.stdout.write(f'Creating {num_users} users...')
        users = []
        for i in range(num_users):
            username = f'user_{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'user{i+1}@example.com',
                    password='testpass123'
                )
                # Create profile
                Profile.objects.create(
                    user=user,
                    country=['USA', 'UK', 'Canada', 'Australia', 'Germany'][i % 5],
                    city=['New York', 'London', 'Toronto', 'Sydney', 'Berlin'][i % 5],
                    about_me=f'Bio of user {i+1}'
                )
                users.append(user)
            else:
                users.append(User.objects.get(username=username))

        self.stdout.write(f'✓ Created {len(users)} users')

        # Create channels
        self.stdout.write(f'Creating {num_channels} channels...')
        channels = []
        channels_per_user = max(1, num_channels // num_users)
        for i in range(num_channels):
            user = users[i % len(users)]
            channel_count = Channel.objects.filter(owner=user).count()
            
            # Skip if user already has max channels (10)
            if channel_count >= 10:
                continue
            
            channel = Channel.objects.create(
                owner=user,
                name=f'Channel {i+1}',
                intro=f'Introduction to channel {i+1}',
                description=f'This is the description for channel {i+1}. It contains interesting content about topic {i+1}.',
            )
            channels.append(channel)

        self.stdout.write(f'✓ Created {len(channels)} channels')

        # Create posts
        self.stdout.write(f'Creating {num_posts} posts...')
        posts_created = 0
        for i in range(num_posts):
            channel = channels[i % len(channels)] if channels else None
            if not channel:
                break
            
            # Check if channel already has max posts (100)
            post_count = Post.objects.filter(channel=channel).count()
            if post_count >= 100:
                # Find a channel with available space
                available_channels = [c for c in channels if Post.objects.filter(channel=c).count() < 100]
                if not available_channels:
                    break
                channel = random.choice(available_channels)

            author = channel.owner  # Posts authored by channel owner
            post = Post.objects.create(
                channel=channel,
                author=author,
                title=f'Post {i+1} in {channel.name}',
                body=f'This is the content of post {i+1}. ' * 10,  # Repeat to make it longer
            )
            posts_created += 1

        self.stdout.write(f'✓ Created {posts_created} posts')
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
