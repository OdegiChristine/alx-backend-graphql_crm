import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


# ==========================
# Types
# ==========================
class CustomerType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    phone = graphene.String()


class ProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    price = graphene.Float()
    stock = graphene.Int()


class OrderType(graphene.ObjectType):
    id = graphene.ID()
    customer = graphene.Field(CustomerType)
    products = graphene.List(ProductType)
    total_amount = graphene.Float()
    order_date = graphene.DateTime()


# ==========================
# Mutations
# ==========================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # --- Validation ---
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="Email already exists.")

        if phone:
            import re
            pattern = r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(pattern, phone):
                return CreateCustomer(success=False, message="Invalid phone format.")

        # --- Create customer ---
        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, success=True, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.NonNull(
                graphene.InputObjectType(
                    "CustomerInput",
                    name=graphene.String(required=True),
                    email=graphene.String(required=True),
                    phone=graphene.String(),
                )
            )
        )

    created_customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, customers):
        created = []
        errors = []

        for data in customers:
            try:
                if Customer.objects.filter(email=data["email"]).exists():
                    errors.append(f"Email already exists: {data['email']}")
                    continue

                phone = data.get("phone")
                if phone:
                    import re
                    pattern = r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$"
                    if not re.match(pattern, phone):
                        errors.append(f"Invalid phone format: {phone}")
                        continue

                customer = Customer.objects.create(**data)
                created.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(created_customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, price, stock):
        if price <= 0:
            return CreateProduct(success=False, message="Price must be positive.")
        if stock < 0:
            return CreateProduct(success=False, message="Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product, success=True, message="Product created successfully.")


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(success=False, message="Invalid customer ID.")

        if not product_ids:
            return CreateOrder(success=False, message="At least one product is required.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            return CreateOrder(success=False, message="Some product IDs are invalid.")

        total_amount = sum([p.price for p in products])
        order = Order.objects.create(
            customer=customer,
            order_date=order_date or timezone.now(),
            total_amount=total_amount,
        )
        order.products.set(products)

        return CreateOrder(order=order, success=True, message="Order created successfully.")


# --------------------------
# Query with Filters
# --------------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


# ==========================
# Root Mutation
# ==========================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
