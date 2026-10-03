from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import AdoptionRequest, Favorite, Pet


class AdoptionTestMixin:
    def setUp(self):
        self.user = User.objects.create_user("rahim", "rahim@example.com", "strong-pass-123")
        self.other_user = User.objects.create_user("maliha", "maliha@example.com", "strong-pass-123")
        self.staff = User.objects.create_superuser("admin", "admin@example.com", "strong-pass-123")
        self.pet = Pet.objects.create(
            name="Max", animal_type="Dog", breed="Golden Retriever", age=2,
            gender="Male", location="Dhaka", description="Friendly and playful.",
        )

    def application(self, user=None, pet=None, **kwargs):
        values = {
            "user": user or self.user, "pet": pet or self.pet, "phone": "01700000000",
            "address": "Dhaka", "reason": "A loving home", "previous_pet_experience": True,
        }
        values.update(kwargs)
        return AdoptionRequest.objects.create(**values)


class ModelBusinessRuleTests(AdoptionTestMixin, TestCase):
    def test_duplicate_pending_request_is_rejected(self):
        self.application()
        with self.assertRaises(ValidationError):
            self.application()

    def test_adopted_pet_rejects_new_pending_request(self):
        self.pet.status = Pet.Status.ADOPTED
        self.pet.save()
        with self.assertRaises(ValidationError):
            self.application()

    def test_only_available_pet_accepts_new_request(self):
        self.pet.status = Pet.Status.PENDING
        self.pet.save()
        with self.assertRaises(ValidationError):
            self.application()

    def test_approval_adopts_pet_and_rejects_other_pending_requests(self):
        winner = self.application()
        other = self.application(user=self.other_user)
        winner.status = AdoptionRequest.Status.APPROVED
        winner.save()
        self.pet.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.pet.status, Pet.Status.ADOPTED)
        self.assertEqual(other.status, AdoptionRequest.Status.REJECTED)


class WebsiteTests(AdoptionTestMixin, TestCase):
    def test_pet_search_and_filters(self):
        response = self.client.get(reverse("pet-list"), {"search": "golden", "gender": "Male"})
        self.assertContains(response, "Max")
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_login_required_for_application(self):
        response = self.client.get(reverse("apply-for-adoption", args=[self.pet.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('apply-for-adoption', args=[self.pet.pk])}")

    def test_user_can_apply_and_see_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("apply-for-adoption", args=[self.pet.pk]), {
            "phone": "01700000000", "address": "Dhaka", "reason": "Companionship",
            "previous_pet_experience": "on", "message": "Ready to welcome Max.",
        })
        self.assertRedirects(response, reverse("dashboard"))
        self.assertContains(self.client.get(reverse("dashboard")), "Max")

    def test_favorite_toggle(self):
        self.client.force_login(self.user)
        self.client.post(reverse("toggle-favorite", args=[self.pet.pk]))
        self.assertTrue(Favorite.objects.filter(user=self.user, pet=self.pet).exists())
        self.client.post(reverse("toggle-favorite", args=[self.pet.pk]))
        self.assertFalse(Favorite.objects.filter(user=self.user, pet=self.pet).exists())


class ApiTests(AdoptionTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.api = APIClient()

    def test_public_can_search_pets(self):
        response = self.api.get("/api/pets/", {"search": "golden"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_non_staff_cannot_create_pet(self):
        self.api.force_authenticate(self.user)
        response = self.api.post("/api/pets/", {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_only_sees_own_applications(self):
        own = self.application()
        self.application(user=self.other_user)
        self.api.force_authenticate(self.user)
        response = self.api.get("/api/adoptions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own.pk)

    def test_token_authentication(self):
        token = Token.objects.create(user=self.user)
        self.api.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.api.get("/api/adoptions/").status_code, 200)
