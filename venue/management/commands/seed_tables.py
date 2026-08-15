from django.core.management.base import BaseCommand
from django.db import transaction

from venue.models import Table, Zone

# (zone name, order, label prefix, how many tables)
LAYOUT = [
    ("Terasa A", 1, "A", 15),
    ("Terasa B", 2, "B", 15),
    ("Park", 3, "P", 10),
    ("Unutra", 4, "U", 10),
]


class Command(BaseCommand):
    help = "Mbush zonat dhe tavolinat fillestare (Terasa A/B, Park, Unutra)."

    @transaction.atomic
    def handle(self, *args, **options):
        created_zones = 0
        created_tables = 0

        for zone_name, order, prefix, count in LAYOUT:
            zone, was_created = Zone.objects.get_or_create(
                name=zone_name, defaults={"order": order}
            )
            if was_created:
                created_zones += 1

            for i in range(1, count + 1):
                _, was_created = Table.objects.get_or_create(
                    zone=zone, label=f"{prefix}{i}", defaults={"order": i}
                )
                if was_created:
                    created_tables += 1

        self.stdout.write(self.style.SUCCESS(
            f"U krijuan {created_zones} zona të reja dhe {created_tables} tavolina të reja."
        ))
