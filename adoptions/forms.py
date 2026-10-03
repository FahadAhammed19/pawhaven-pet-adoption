from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import AdoptionRequest


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")


class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ("address", "phone", "reason", "previous_pet_experience", "message")
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "reason": forms.Textarea(attrs={"rows": 4}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {"previous_pet_experience": "I have owned a pet before"}
