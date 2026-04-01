from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Report duplicate user emails (case-insensitive)."

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.exclude(email__isnull=True).exclude(email="").order_by("id")

        grouped = defaultdict(list)
        for user in users:
            grouped[user.email.strip().lower()].append(user)

        duplicates = {email: items for email, items in grouped.items() if len(items) > 1}

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicate emails found."))
            self.stdout.write(f"Checked {users.count()} users with non-empty emails.")
            return

        self.stdout.write(self.style.WARNING(f"Found {len(duplicates)} duplicate email group(s):"))
        for email, items in sorted(duplicates.items()):
            details = ", ".join([f"{u.username}(id={u.id})" for u in items])
            self.stdout.write(f"- {email}: {details}")

        self.stdout.write("")
        self.stdout.write(f"Checked {users.count()} users with non-empty emails.")
