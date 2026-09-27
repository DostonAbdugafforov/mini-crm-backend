import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class LeadSource(models.TextChoices):
    WEBSITE = "WEBSITE", "Website"
    REFERRAL = "REFERRAL", "Referral"
    ADS = "ADS", "Ads"
    COLD_CALL = "COLD_CALL", "Cold call"
    OTHER = "OTHER", "Other"


class LeadStatus(models.TextChoices):
    NEW = "NEW", "New"
    CONTACTED = "CONTACTED", "Contacted"
    QUALIFIED = "QUALIFIED", "Qualified"
    WON = "WON", "Won"
    LOST = "LOST", "Lost"


class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(
        max_length=20, choices=LeadSource.choices, default=LeadSource.OTHER
    )
    status = models.CharField(
        max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW
    )
    note = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"

    def clean(self):
        if not self.phone and not self.email:
            raise ValidationError(
                "phone yoki email kamida bittasi kiritilishi shart."
            )

    def save(self, *args, **kwargs):
        # clean() Django tomonidan avtomatik chaqirilmaydi (faqat ModelForm/admin
        # orqali chaqiriladi), shuning uchun to'g'ridan-to'g'ri save() chaqirilganda
        # ham (masalan admin panel, shell, boshqa kod orqali) validatsiya ishlashi
        # uchun full_clean() ni bu yerda majburiy qilamiz.
        self.full_clean()
        super().save(*args, **kwargs)


class LeadActivity(models.Model):
    class Action(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPDATED = "UPDATED", "Updated"
        STATUS_CHANGED = "STATUS_CHANGED", "Status changed"
        DELETED = "DELETED", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name="activities", null=True
    )
    # lead o'chirilganda ham tarix saqlanib qolishi uchun ID'sini alohida
    # saqlaymiz (lead FK CASCADE bilan o'chib ketishi mumkin).
    lead_id_snapshot = models.UUIDField(null=True, blank=True)
    lead_name_snapshot = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Lead activities"

    def __str__(self):
        return f"{self.action} - {self.lead_name_snapshot or self.lead_id}"