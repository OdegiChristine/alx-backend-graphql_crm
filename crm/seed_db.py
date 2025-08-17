import random
from django.utils import timezone
from .models import Customer, Product, Order


def run():
    """Seed the database with sample Customers, Products, and Orders."""
    # Clear old data
    print("Deleting old data...")
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()

    # Create customers
    print("Creating customers...")
    customers = [
        Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Charlie Brown", email="charlie@example.com"),
    ]
    Customer.objects.bulk_create(customers)

    # Create products
    print("Creating products...")
    products = [
        Product(name="Laptop", price=1200.00, stock=10),
        Product(name="Smartphone", price=800.00, stock=20),
        Product(name="Headphones", price=150.00, stock=30),
        Product(name="Keyboard", price=75.00, stock=15),
        Product(name="Mouse", price=40.00, stock=25),
    ]
    Product.objects.bulk_create(products)

    # Fetch saved customers & products
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    # Create random orders
    print("Creating orders...")
    for i in range(5):
        customer = random.choice(customers)
        order = Order.objects.create(
            customer=customer,
            order_date=timezone.now(),
        )
        selected_products = random.sample(products, k=random.randint(1, 3))
        order.products.set(selected_products)
        order.save()

    print("✅ Database seeded successfully!")
