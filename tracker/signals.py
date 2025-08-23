import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EcoAction
from .utils.geo import enrich_region

logger = logging.getLogger('tracker')  # Matches logger name in settings.py


@receiver(post_save, sender=EcoAction)
def auto_enrich_region(sender, instance, created, **kwargs):
    if not instance.location:
        logger.info(
            f"EcoAction {instance.id}"
            f" skipped enrichment: no location provided.")
        return

    from tracker.models import RegionInfo
    region = RegionInfo.objects.filter(name=instance.location).first()
    if region and region.latitude:
        logger.info(
            f"EcoAction {instance.id} location"
            f" '{instance.location}' already enriched.")
        return

    try:
        enrich_region(instance.location)
        logger.info(
            f"EcoAction {instance.id} enriched"
            f" location '{instance.location}'.")
    except Exception as e:
        logger.warning(
            f"⚠️ Failed to enrich location '{instance.location}'"
            f" for EcoAction {instance.id}: {e}")
