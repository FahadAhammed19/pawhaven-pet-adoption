from django.db import transaction
from rest_framework import serializers

from .models import AdoptionRequest, Pet


class PetSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = (
            "id", "name", "animal_type", "breed", "age", "gender", "location",
            "description", "image", "image_url", "status", "created_at",
        )
        read_only_fields = ("id", "image_url", "created_at")

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    pet_name = serializers.CharField(source="pet.name", read_only=True)

    class Meta:
        model = AdoptionRequest
        fields = (
            "id", "user", "pet", "pet_name", "phone", "address", "reason",
            "previous_pet_experience", "message", "status", "created_at",
        )
        read_only_fields = ("id", "user", "pet_name", "created_at")

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if not request or not request.user.is_staff:
            fields["status"].read_only = True
        return fields

    def validate(self, attrs):
        request = self.context["request"]
        pet = attrs.get("pet") or getattr(self.instance, "pet", None)
        if not self.instance and pet.status != Pet.Status.AVAILABLE:
            raise serializers.ValidationError({"pet": "This pet is not currently available for adoption."})
        duplicate = AdoptionRequest.objects.filter(
            user=request.user, pet=pet, status=AdoptionRequest.Status.PENDING
        )
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError("You already have a pending request for this pet.")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            pet = Pet.objects.select_for_update().get(pk=validated_data["pet"].pk)
            if pet.status != Pet.Status.AVAILABLE:
                raise serializers.ValidationError({"pet": "This pet is not currently available for adoption."})
            return AdoptionRequest.objects.create(user=self.context["request"].user, **validated_data)
