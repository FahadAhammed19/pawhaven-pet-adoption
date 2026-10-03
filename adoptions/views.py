from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdoptionRequestForm, RegisterForm
from .models import AdoptionRequest, Favorite, Pet


def _filtered_pets(request):
    pets = Pet.objects.all()
    search = request.GET.get("search", "").strip()
    if search:
        pets = pets.filter(
            Q(name__icontains=search)
            | Q(animal_type__icontains=search)
            | Q(breed__icontains=search)
            | Q(location__icontains=search)
        )
    for field in ("animal_type", "gender", "location", "status"):
        value = request.GET.get(field, "").strip()
        if value:
            pets = pets.filter(**{f"{field}__iexact": value})
    return pets


def home(request):
    return render(request, "adoptions/home.html", {"featured_pets": Pet.objects.filter(status=Pet.Status.AVAILABLE)[:3]})


def pet_list(request):
    paginator = Paginator(_filtered_pets(request), 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "animal_types": Pet.AnimalType.choices,
        "genders": Pet.Gender.choices,
        "statuses": Pet.Status.choices,
    }
    return render(request, "adoptions/pet_list.html", context)


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, pet=pet).exists()
    return render(request, "adoptions/pet_detail.html", {"pet": pet, "is_favorite": is_favorite})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account is ready.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "adoptions/profile.html")


@login_required
def apply_for_adoption(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if pet.status != Pet.Status.AVAILABLE:
        messages.error(request, "This pet is not currently available for adoption.")
        return redirect("pet-detail", pk=pk)
    if AdoptionRequest.objects.filter(user=request.user, pet=pet, status=AdoptionRequest.Status.PENDING).exists():
        messages.warning(request, "You already have a pending request for this pet.")
        return redirect("dashboard")

    form = AdoptionRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                locked_pet = Pet.objects.select_for_update().get(pk=pet.pk)
                if locked_pet.status != Pet.Status.AVAILABLE:
                    messages.error(request, "This pet is no longer available for adoption.")
                    return redirect("pet-detail", pk=pk)
                adoption = form.save(commit=False)
                adoption.user = request.user
                adoption.pet = locked_pet
                adoption.save()
            messages.success(request, "Your adoption application was submitted.")
            return redirect("dashboard")
        except IntegrityError:
            messages.error(request, "You already have a pending request for this pet.")
            return redirect("dashboard")
    return render(request, "adoptions/adoption_form.html", {"form": form, "pet": pet})


@login_required
def dashboard(request):
    applications = AdoptionRequest.objects.filter(user=request.user).select_related("pet")
    return render(request, "adoptions/dashboard.html", {"applications": applications})


@login_required
def toggle_favorite(request, pk):
    if request.method != "POST":
        return redirect("pet-detail", pk=pk)
    pet = get_object_or_404(Pet, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, pet=pet)
    if created:
        messages.success(request, f"{pet.name} was added to your favorites.")
    else:
        favorite.delete()
        messages.info(request, f"{pet.name} was removed from your favorites.")
    return redirect(request.POST.get("next") or "pet-detail", pk=pk)


@login_required
def favorites(request):
    favorites_qs = Favorite.objects.filter(user=request.user).select_related("pet")
    return render(request, "adoptions/favorites.html", {"favorites": favorites_qs})
