from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StaffProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_staff_profile(sender, instance, created, **kwargs):
    if not created:
        return
    role = StaffProfile.ADMIN if instance.is_superuser else StaffProfile.KONOBAR
    StaffProfile.objects.get_or_create(user=instance, defaults={"role": role})
