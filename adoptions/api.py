from rest_framework import filters, permissions, viewsets

from .models import AdoptionRequest, Pet
from .serializers import AdoptionRequestSerializer, PetSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (request.user.is_authenticated and request.user.is_staff)


class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "animal_type", "breed", "location", "description"]

    def get_queryset(self):
        queryset = Pet.objects.all()
        for field in ("animal_type", "breed", "gender", "location", "status"):
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{f"{field}__iexact": value})
        return queryset


class AdoptionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        queryset = AdoptionRequest.objects.select_related("pet", "user")
        return queryset if self.request.user.is_staff else queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
