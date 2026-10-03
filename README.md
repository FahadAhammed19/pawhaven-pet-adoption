# PawHaven - Pet Adoption & Rescue Platform

PawHaven is a complete Django assignment project with a responsive template-based website and a Django REST Framework API. Visitors can browse and filter pets; registered users can apply for adoption, track requests, manage favorites, and view their profile; staff manage pets and applications through Django Admin.

## Assignment coverage

- Registration, login, logout, and profile
- Pet cards, details, image upload, search, multi-field filters, and pagination
- Adoption form and user dashboard with Pending, Approved, and Rejected states
- Business rules preventing applications for adopted pets and duplicate active requests
- Approval workflow that marks the pet Adopted and rejects its other pending requests
- Django Admin pet and adoption-request management
- REST CRUD for pets, authenticated adoption APIs, search/filtering, and API pagination
- Token and session authentication
- Bonus favorites and fixed pet categories
- Automated tests and database migration

## Quick start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Admin is at `http://127.0.0.1:8000/admin/`.

For macOS/Linux, activate the environment with `source .venv/bin/activate`.

## API

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/pets/` | Public |
| GET | `/api/pets/<id>/` | Public |
| POST | `/api/pets/` | Staff only |
| PUT, PATCH, DELETE | `/api/pets/<id>/` | Staff only |
| GET, POST | `/api/adoptions/` | Authenticated; users see only their own |
| GET, PUT, PATCH | `/api/adoptions/<id>/` | Owner or staff queryset; only staff can change status |
| POST | `/api/token/` | Returns an API token for username/password |

Pet queries support `search`, `animal_type`, `breed`, `gender`, `location`, `status`, and `page`:

```text
/api/pets/?search=golden
/api/pets/?animal_type=Dog&gender=Male&location=Dhaka
/api/pets/?page=2
```

Use a token with `Authorization: Token YOUR_TOKEN`.

## Important implementation notes

- The conditional database constraint permits historical rejected/approved records while allowing only one pending request per user and pet.
- Approval runs in a transaction, updates the pet to Adopted, and rejects other pending requests for that pet.
- New HTML and API applications lock the pet row during creation, reducing race-condition risk.
- Change `SECRET_KEY`, set `DEBUG = False`, configure `ALLOWED_HOSTS`, and use production media/static storage before deployment.

## Run the tests

```powershell
python manage.py test
python manage.py check
```

## Suggested GitHub submission

Create an empty GitHub repository, then from this folder run:

```powershell
git init
git add .
git commit -m "Complete pet adoption platform assignment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

The GitHub URL must be created under the student's own account, so it is the only submission item not generated locally.
