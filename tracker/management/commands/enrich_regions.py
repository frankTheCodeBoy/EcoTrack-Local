from django.core.management.base import BaseCommand
from tracker.models import EcoAction, RegionInfo
from tracker.utils.geo import enrich_region


class Command(BaseCommand):
    help = "Enrich unique EcoAction locations with geocoded data and emoji"

    def handle(self, *args, **options):
        locations = (
            EcoAction.objects.exclude(location__isnull=True)
            .exclude(location__exact='')
            .values_list('location', flat=True)
            .distinct()
        )

        enriched = 0
        skipped = 0
        failed = []

        for loc in locations:
            loc = loc.strip()
            if not loc:
                continue

            region = RegionInfo.objects.filter(name=loc).first()
            if region and region.latitude:
                self.stdout.write(self.style.NOTICE(
                    f"✔️ Already enriched: {loc}"))
                skipped += 1
                continue

            info = enrich_region(loc)
            if info and info.latitude:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Enriched: {loc} → {info.emoji}"
                    f" ({info.latitude}, {info.longitude})"))
                enriched += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Could not geocode: {loc}"))
                failed.append(loc)

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done! {enriched} enriched, {skipped} skipped."))
        if failed:
            self.stdout.write(self.style.WARNING(
                f"⚠️ {len(failed)} locations failed to geocode."))
            with open("failed_geocodes.txt", "w") as f:
                for loc in failed:
                    f.write(f"{loc}\n")
