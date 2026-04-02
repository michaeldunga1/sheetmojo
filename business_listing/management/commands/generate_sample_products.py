import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from business_listing.models import BusinessDetails, Product


class Command(BaseCommand):
    help = "Generate sample products, optionally rebalance product distribution, and create placeholder images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of sample products to create (default: 100).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional random seed for reproducible data generation.",
        )
        parser.add_argument(
            "--rebalance",
            action="store_true",
            help="Reassign all products so selected businesses each have between min/max products.",
        )
        parser.add_argument(
            "--min-per-business",
            type=int,
            default=1,
            help="Minimum products per business when rebalancing (default: 1).",
        )
        parser.add_argument(
            "--max-per-business",
            type=int,
            default=3,
            help="Maximum products per business when rebalancing (default: 3).",
        )
        parser.add_argument(
            "--with-images",
            action="store_true",
            help="Create placeholder images for products that do not have images.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]
        rebalance = options["rebalance"]
        with_images = options["with_images"]
        min_per_business = options["min_per_business"]
        max_per_business = options["max_per_business"]

        if seed is not None:
            random.seed(seed)

        if count < 0:
            self.stderr.write(self.style.ERROR("--count must be 0 or greater."))
            return

        if min_per_business < 1 or max_per_business < 1:
            self.stderr.write(self.style.ERROR("--min-per-business and --max-per-business must be at least 1."))
            return

        if min_per_business > max_per_business:
            self.stderr.write(self.style.ERROR("--min-per-business cannot be greater than --max-per-business."))
            return

        businesses = list(BusinessDetails.objects.all().order_by("id"))
        if not businesses:
            fallback = BusinessDetails.objects.create(
                business_name="Sample Business",
                category="General",
                country="US",
                city="Austin",
                short_description="Auto-generated for sample products",
            )
            businesses = [fallback]
            self.stdout.write(self.style.WARNING("No businesses found. Created fallback business: Sample Business"))

        name_pool = [
            "Classic Bread",
            "Sourdough Loaf",
            "Chocolate Cake",
            "Vanilla Cupcake",
            "Coffee Beans",
            "Tea Pack",
            "Office Chair",
            "Wooden Desk",
            "LED Lamp",
            "Smartphone Case",
            "Bluetooth Speaker",
            "Running Shoes",
            "Leather Wallet",
            "Backpack",
            "Water Bottle",
            "Notebook Set",
            "Gaming Mouse",
            "USB Cable",
            "Phone Charger",
            "Desk Organizer",
        ]
        category_pool = [
            "Bakery",
            "Groceries",
            "Electronics",
            "Furniture",
            "Accessories",
            "Stationery",
            "Fashion",
            "Home Goods",
            "Fitness",
            "Beverages",
        ]
        desc_pool = [
            "High quality product for everyday use.",
            "Popular choice among returning customers.",
            "Durable and thoughtfully designed.",
            "Limited stock available this week.",
            "Great value for the listed price.",
            "Trusted by local buyers and businesses.",
        ]
        terms_pool = list(Product.TermsOfSale.values)
        currency_pool = list(Product.Currency.values)

        products_before = Product.objects.count()
        created = 0
        for i in range(count):
            business = random.choice(businesses)
            base_name = random.choice(name_pool)
            category = random.choice(category_pool)
            price = Decimal(str(round(random.uniform(5, 500), 2)))

            Product.objects.create(
                business=business,
                product_name=f"{base_name} #{products_before + i + 1}",
                product_category=category,
                price=price,
                currency=random.choice(currency_pool),
                product_description=random.choice(desc_pool),
                terms_of_sale=random.choice(terms_pool),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} product(s)."))

        if rebalance:
            self._rebalance_products(min_per_business, max_per_business)

        if with_images:
            generated = self._create_placeholder_images()
            self.stdout.write(self.style.SUCCESS(f"Generated {generated} placeholder image(s)."))

        self.stdout.write(self.style.SUCCESS(f"Total products: {Product.objects.count()}"))

    def _rebalance_products(self, min_per_business, max_per_business):
        products = list(Product.objects.select_related("business").all().order_by("id"))
        businesses = list(BusinessDetails.objects.all().order_by("id"))
        total_products = len(products)

        if not products or not businesses:
            self.stdout.write(self.style.WARNING("Skipping rebalance: missing products or businesses."))
            return

        min_businesses_needed = (total_products + max_per_business - 1) // max_per_business
        max_businesses_allowed = max(1, total_products // min_per_business)

        business_count = min(len(businesses), max_businesses_allowed)
        business_count = max(min_businesses_needed, business_count)
        business_count = min(business_count, len(businesses))

        selected_businesses = random.sample(businesses, business_count)
        counts = [min_per_business] * business_count
        assigned = sum(counts)

        if assigned > total_products:
            counts = [0] * business_count
            assigned = 0

        remaining = total_products - assigned
        while remaining > 0:
            idx = random.randrange(business_count)
            if counts[idx] < max_per_business:
                counts[idx] += 1
                remaining -= 1

        assignment = []
        for business, amount in zip(selected_businesses, counts):
            assignment.extend([business] * amount)

        random.shuffle(assignment)
        updated = 0
        for product, business in zip(products, assignment):
            if product.business_id != business.id:
                product.business = business
                product.save(update_fields=["business"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Rebalanced products across {business_count} business(es)."))
        self.stdout.write(f"Business assignments updated: {updated}")

    def _create_placeholder_images(self):
        from PIL import Image

        media_products_dir = Path(settings.MEDIA_ROOT) / "products"
        media_products_dir.mkdir(parents=True, exist_ok=True)

        generated = 0
        for product in Product.objects.filter(product_image=""):
            filename = f"sample_product_{product.id}.png"
            file_path = media_products_dir / filename

            color = tuple(random.randint(40, 215) for _ in range(3))
            image = Image.new("RGB", (1200, 800), color=color)
            image.save(file_path, format="PNG")

            product.product_image = f"products/{filename}"
            product.save(update_fields=["product_image"])
            generated += 1

        return generated
