from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q


class Pet(models.Model):
    class AnimalType(models.TextChoices):
        DOG = "Dog", "Dog"
        CAT = "Cat", "Cat"
        BIRD = "Bird", "Bird"
        RABBIT = "Rabbit", "Rabbit"
        OTHER = "Other", "Other"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        UNKNOWN = "Unknown", "Unknown"

    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        PENDING = "Pending", "Adoption pending"
        ADOPTED = "Adopted", "Adopted"

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=20, choices=AnimalType.choices)
    breed = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to="pets/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def __str__(self):
        return self.name


class AdoptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adoption_requests")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="adoption_requests")
    phone = models.CharField(max_length=30)
    address = models.TextField()
    reason = models.TextField()
    previous_pet_experience = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "pet"],
                condition=Q(status="Pending"),
                name="one_pending_request_per_user_pet",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.pet} ({self.status})"

    def clean(self):
        super().clean()
        if self.status == self.Status.PENDING and self.pet_id and self.pet.status != Pet.Status.AVAILABLE:
            raise ValidationError({"pet": "This pet is not currently available for adoption."})
        if self.status == self.Status.APPROVED and self.pet_id:
            already_approved = AdoptionRequest.objects.filter(
                pet_id=self.pet_id, status=self.Status.APPROVED
            ).exclude(pk=self.pk)
            if already_approved.exists():
                raise ValidationError({"status": "This pet already has an approved application."})
        duplicate = AdoptionRequest.objects.filter(
            user_id=self.user_id, pet_id=self.pet_id, status=self.Status.PENDING
        ).exclude(pk=self.pk)
        if self.user_id and self.pet_id and duplicate.exists():
            raise ValidationError("You already have a pending request for this pet.")

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            result = super().save(*args, **kwargs)
            if self.status == self.Status.APPROVED:
                Pet.objects.filter(pk=self.pet_id).update(status=Pet.Status.ADOPTED)
                AdoptionRequest.objects.filter(
                    pet_id=self.pet_id, status=self.Status.PENDING
                ).exclude(pk=self.pk).update(status=self.Status.REJECTED)
            return result


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "pet"], name="unique_favorite")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} likes {self.pet}"
