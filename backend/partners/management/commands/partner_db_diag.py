from django.core.management.base import BaseCommand
from django.db.models import Q
from partners.models import Partner

class Command(BaseCommand):
    help = "Read-only diagnostic for partner application records"

    def handle(self, *args, **options):
        allq = Partner.objects.all()
        direct = allq.filter(source="public_partner_application")
        legacy = allq.filter(
            ~Q(representative_name=""),
            ~Q(contact_email=""),
            is_affiliated=True,
        )
        union = allq.filter(
            Q(source="public_partner_application")
            | (
                ~Q(representative_name="")
                & ~Q(contact_email="")
                & Q(is_affiliated=True)
            )
        ).distinct()

        self.stdout.write(f"PARTNER_DB_TOTAL={allq.count()}")
        self.stdout.write(f"DIRECT_SOURCE_COUNT={direct.count()}")
        self.stdout.write(f"LEGACY_APPLICATION_CANDIDATES={legacy.count()}")
        self.stdout.write(f"APPLICATION_UNION_COUNT={union.count()}")

        for p in union.order_by("id"):
            self.stdout.write(
                "ROW|"
                f"id={p.id}|name={p.name}|representative={p.representative_name}|"
                f"email={p.contact_email}|status={p.application_status}|"
                f"active={p.is_active}|source={p.source}|created_at={p.created_at.isoformat()}"
            )
