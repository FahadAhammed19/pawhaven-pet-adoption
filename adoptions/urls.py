from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pets/", views.pet_list, name="pet-list"),
    path("pets/<int:pk>/", views.pet_detail, name="pet-detail"),
    path("pets/<int:pk>/apply/", views.apply_for_adoption, name="apply-for-adoption"),
    path("pets/<int:pk>/favorite/", views.toggle_favorite, name="toggle-favorite"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("favorites/", views.favorites, name="favorites"),
]
