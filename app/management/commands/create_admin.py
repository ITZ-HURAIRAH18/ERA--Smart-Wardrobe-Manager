from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Customer

class Command(BaseCommand):
    help = 'Create an admin superuser and customer account'

    def handle(self, *args, **options):
        # Admin user details
        email = 'admin@gmail.com'
        first_name = 'Abu'
        last_name = 'Hurairah'
        phone = '03118756988'
        password = '12345678'
        username = 'admin'

        # Create Django superuser (for admin site login)
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            self.stdout.write(self.style.SUCCESS(f'✓ Django Superuser created: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Django Superuser "{username}" already exists'))

        # Create Customer account
        if not Customer.objects.filter(email=email).exists():
            customer = Customer.objects.create(
                fname=first_name,
                lname=last_name,
                email=email,
                phone=phone,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Customer account created: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Customer account "{email}" already exists'))

        self.stdout.write(self.style.SUCCESS('Admin setup completed!'))
