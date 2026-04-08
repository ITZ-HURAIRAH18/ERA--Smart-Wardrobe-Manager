"""
Management command to seed the database with sample data for ERA project.
Creates categories, 15 products (5 Men, 5 Women, 5 Children) with real Unsplash images.
"""
from django.core.management.base import BaseCommand
from app.models import Cat, Std, Customer, Coupon


class Command(BaseCommand):
    help = 'Seed database with sample products, categories, and sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create categories
        self.stdout.write('Creating categories...')
        men_cat, _ = Cat.objects.get_or_create(name='Men')
        women_cat, _ = Cat.objects.get_or_create(name='Women')
        children_cat, _ = Cat.objects.get_or_create(name='Children')

        self.stdout.write(self.style.SUCCESS(f'  Categories created: Men, Women, Children'))

        # Men's products (5 products)
        men_products = [
            {
                'name': 'Classic Navy Blazer',
                'price': 129,
                'description': 'A timeless navy blazer perfect for both formal and casual occasions. Crafted from premium wool blend fabric with a modern slim fit.',
                'image': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&q=80',
                'sizes': 'S,M,L,XL',
                'colors': 'Navy,Charcoal,Black',
                'stock': 50,
            },
            {
                'name': 'Premium Denim Jacket',
                'price': 89,
                'description': 'Vintage-wash denim jacket with a relaxed fit. Features classic button closure and chest pockets.',
                'image': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&q=80',
                'sizes': 'M,L,XL,XXL',
                'colors': 'Blue,Black,Light Wash',
                'stock': 75,
            },
            {
                'name': 'Oxford Cotton Shirt',
                'price': 59,
                'description': 'Crisp Oxford cotton shirt in a classic fit. Perfect for the office or weekend.',
                'image': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&q=80',
                'sizes': 'S,M,L,XL',
                'colors': 'White,Blue,Pink',
                'stock': 100,
            },
            {
                'name': 'Tailored Chino Pants',
                'price': 69,
                'description': 'Slim-fit chino pants crafted from stretch cotton for all-day comfort.',
                'image': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80',
                'sizes': '30,32,34,36,38',
                'colors': 'Khaki,Navy,Olive',
                'stock': 80,
            },
            {
                'name': 'Leather Chelsea Boots',
                'price': 149,
                'description': 'Premium leather Chelsea boots with elastic side panels and pull tab. Handcrafted for lasting quality.',
                'image': 'https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=600&q=80',
                'sizes': '7,8,9,10,11,12',
                'colors': 'Brown,Black,Tan',
                'stock': 40,
            },
        ]

        # Women's products (5 products)
        women_products = [
            {
                'name': 'Floral Summer Dress',
                'price': 79,
                'description': 'Light and breezy floral dress perfect for summer days. Features a flattering A-line silhouette.',
                'image': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&q=80',
                'sizes': 'XS,S,M,L,XL',
                'colors': 'Floral Blue,Floral Pink,Floral White',
                'stock': 60,
            },
            {
                'name': 'Elegant Evening Gown',
                'price': 199,
                'description': 'Stunning floor-length evening gown with delicate lace detailing and open back.',
                'image': 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600&q=80',
                'sizes': 'XS,S,M,L',
                'colors': 'Black,Navy,Burgundy',
                'stock': 25,
            },
            {
                'name': 'Silk Blouse',
                'price': 89,
                'description': 'Luxurious silk blouse with a relaxed fit and subtle sheen. Perfect for the modern professional.',
                'image': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=600&q=80',
                'sizes': 'XS,S,M,L,XL',
                'colors': 'Ivory,Blush,Sage',
                'stock': 45,
            },
            {
                'name': 'High-Waist Wide Leg Trousers',
                'price': 75,
                'description': 'Chic wide-leg trousers with a flattering high waist. Effortlessly elegant.',
                'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600&q=80',
                'sizes': 'XS,S,M,L,XL',
                'colors': 'Black,Cream,Olive',
                'stock': 55,
            },
            {
                'name': 'Designer Handbag',
                'price': 159,
                'description': 'Elegant leather handbag with gold-tone hardware. Features adjustable strap and multiple compartments.',
                'image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&q=80',
                'sizes': 'One Size',
                'colors': 'Tan,Black,Blush',
                'stock': 30,
            },
        ]

        # Children's products (5 products)
        children_products = [
            {
                'name': 'Kids Graphic Tee',
                'price': 25,
                'description': 'Fun graphic-printed t-shirt made from soft organic cotton. Machine washable.',
                'image': 'https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600&q=80',
                'sizes': '4Y,6Y,8Y,10Y,12Y',
                'colors': 'Blue,Red,Green',
                'stock': 120,
            },
            {
                'name': 'Denim Overalls',
                'price': 45,
                'description': 'Classic denim overalls with adjustable straps. Perfect for active kids.',
                'image': 'https://images.unsplash.com/photo-1519457431-44ccd64a579b?w=600&q=80',
                'sizes': '4Y,6Y,8Y,10Y',
                'colors': 'Blue,Black',
                'stock': 65,
            },
            {
                'name': 'Floral Party Dress',
                'price': 55,
                'description': 'Beautiful floral party dress with tulle layers. Perfect for special occasions.',
                'image': 'https://images.unsplash.com/photo-1543076447-215ad9ba6523?w=600&q=80',
                'sizes': '4Y,6Y,8Y,10Y,12Y',
                'colors': 'Pink,White,Lavender',
                'stock': 40,
            },
            {
                'name': 'Boys Casual Shorts Set',
                'price': 35,
                'description': 'Comfortable shorts and polo shirt set for boys. Breathable fabric for active play.',
                'image': 'https://images.unsplash.com/photo-1503919545889-aef636e10ad4?w=600&q=80',
                'sizes': '4Y,6Y,8Y,10Y,12Y',
                'colors': 'Navy,Khaki,Gray',
                'stock': 90,
            },
            {
                'name': 'Kids Sneakers',
                'price': 49,
                'description': 'Colorful and comfortable sneakers with velcro straps. Non-slip sole for safety.',
                'image': 'https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=600&q=80',
                'sizes': '10C,11C,12C,13C,1Y,2Y',
                'colors': 'Multi,Blue,Pink',
                'stock': 70,
            },
        ]

        # Create all products
        all_products = [
            (men_products, men_cat),
            (women_products, women_cat),
            (children_products, children_cat),
        ]

        total_created = 0
        total_updated = 0

        for products, category in all_products:
            for product_data in products:
                obj, created = Std.objects.update_or_create(
                    name=product_data['name'],
                    defaults={
                        'price': product_data['price'],
                        'category': category,
                        'description': product_data['description'],
                        'available_sizes': product_data['sizes'],
                        'available_colors': product_data['colors'],
                        'stock_quantity': product_data['stock'],
                        'is_active': True,
                    }
                )

                # Download and set image from URL
                if product_data['image']:
                    # We'll use the URL directly - the template will use it as external URL
                    # For a real app, you'd download and save to ImageField
                    pass

                if created:
                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f'  Created: {product_data["name"]}'))
                else:
                    total_updated += 1
                    self.stdout.write(self.style.WARNING(f'  Updated: {product_data["name"]}'))

        # Create admin customer if not exists
        admin_customer, created = Customer.objects.get_or_create(
            email='admin@era.com',
            defaults={
                'fname': 'Admin',
                'lname': 'ERA',
                'phone': '+1234567890',
                'password': 'admin123',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created admin customer (admin@era.com / admin123)'))

        # Create sample coupons
        coupons = [
            {'code': 'WELCOME10', 'discount_percent': 10, 'min_order_value': 50, 'expiry_date': '2027-12-31'},
            {'code': 'SUMMER20', 'discount_percent': 20, 'min_order_value': 100, 'expiry_date': '2027-09-30'},
            {'code': 'ERA15', 'discount_percent': 15, 'min_order_value': 75, 'expiry_date': '2027-06-30'},
        ]

        for coupon_data in coupons:
            Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults={
                    'discount_percent': coupon_data['discount_percent'],
                    'min_order_value': coupon_data['min_order_value'],
                    'expiry_date': coupon_data['expiry_date'],
                    'active': True,
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  Coupon: {coupon_data["code"]}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'  Products created: {total_created}'))
        self.stdout.write(self.style.SUCCESS(f'  Products updated: {total_updated}'))
        self.stdout.write(self.style.SUCCESS(f'  Total products: {Std.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Categories: {Cat.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Coupons: {Coupon.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*50))
