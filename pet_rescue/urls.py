from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from adoptions.api import AdoptionRequestViewSet, PetViewSet

router = DefaultRouter()
router.register("pets", PetViewSet, basename="api-pet")
router.register("adoptions", AdoptionRequestViewSet, basename="api-adoption")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", obtain_auth_token, name="api-token"),
    path("api/", include(router.urls)),
    path("", include("adoptions.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
