from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create demo admin users for testing'

    def handle(self, *args, **options):
        # Demo admin users
        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'demo',
                'email': 'demo@example.com',
                'password': 'demo123',
                'is_staff': True,
                'is_superuser': True,
            }
        ]

        for user_data in demo_users:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Skipping...')
                )
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser "{username}" created successfully!')
                )
                self.stdout.write(f'   Email: {user_data["email"]}')
                self.stdout.write(f'   Password: {user_data["password"]}')

        self.stdout.write(
            self.style.SUCCESS('\n✅ Demo admin users are ready!')
        )
        self.stdout.write('\nLogin with:')
        self.stdout.write('  Email: admin@example.com')
        self.stdout.write('  Password: admin123')
