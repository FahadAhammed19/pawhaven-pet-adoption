from django.core.management.base import BaseCommand

from adoptions.models import Pet


PETS = [
    {"name": "Max", "animal_type": "Dog", "breed": "Golden Retriever", "age": 2, "gender": "Male", "location": "Dhaka", "description": "Max is friendly, playful, and happiest around people."},
    {"name": "Luna", "animal_type": "Cat", "breed": "Domestic Shorthair", "age": 1, "gender": "Female", "location": "Chattogram", "description": "Luna is curious, gentle, and loves a sunny windowsill."},
    {"name": "Coco", "animal_type": "Rabbit", "breed": "Mini Lop", "age": 2, "gender": "Female", "location": "Dhaka", "description": "Coco is calm, tidy, and enjoys leafy treats."},
    {"name": "Rio", "animal_type": "Bird", "breed": "Budgerigar", "age": 1, "gender": "Male", "location": "Sylhet", "description": "Rio is social, cheerful, and quick to learn new sounds."},
]


class Command(BaseCommand):
    help = "Create a small set of demo pets without duplicates."

    def handle(self, *args, **options):
        created = 0
        for data in PETS:
            _, was_created = Pet.objects.get_or_create(name=data["name"], defaults=data)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Created {created} demo pet(s)."))
