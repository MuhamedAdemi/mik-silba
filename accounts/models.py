from django.conf import settings
from django.db import models


class StaffProfile(models.Model):
    ADMIN = "ADMIN"
    KONOBAR = "KONOBAR"
    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (KONOBAR, "Konobar"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=KONOBAR)
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emri që shfaqet në ekran (p.sh. te tavolina). Bosh = username.",
    )

    class Meta:
        verbose_name = "Profil stafi"
        verbose_name_plural = "Profilet e stafit"

    def __str__(self):
        return self.display_name or self.user.get_username()

    @property
    def is_admin(self):
        return self.role == self.ADMIN
