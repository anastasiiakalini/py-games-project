# py-games-project

Py Games is a Django web application for browsing and managing video games, game developers, genres, and countries. 
It is a learning project that demonstrates Django models, authentication, 
forms, class-based views, access control, and automated tests.

## Features

- Developer accounts: registration, login, and profile management using a custom user model.
- Game management: authenticated developers can create games and update or delete their own games.
- Catalog browsing: lists and detail pages for games and developers, plus lists of genres and countries.
- Search and filtering: search items by name; browse developers by country and games by genre.
- Pagination: catalog lists display up to five records per page.
- Flexible data entry: add a new genre when creating a game or a new country when registering or updating a developer profile.
- Validation: Django forms check the submitted data.
- Automatic cleanup: signals remove unused genres when games are deleted and unused countries when developers are deleted.
- Tests: Django tests cover selected models, views, forms, authentication, and signals.

## Tech Stack

- Python
- Django 5.2
- SQLite (development database)
- Django templates
- Bootstrap 5 integration via django-crispy-forms and crispy-bootstrap5
- Django Debug Toolbar (development)

## Models

The project includes four main models:

- **Developer** – a custom user who can create and manage games
- **Game** – contains information about a game, including its developer, genres, description, and price
- **Genre** – represents game genres
- **Country** – represents developers' countries

### Relationships:

- **Country → Developer**: one-to-many — a country may have several developers.
- **Developer → Game**: one-to-many — a developer may own several games.
- **Game ↔ Genre**: many-to-many — a game may have several genres, and a genre may belong to several games.


### Permissions
- Registration is available without logging in.
- Catalog and detail views require authentication.
- Only a game's developer can update or delete that game.
- Developers can update or delete only their own profile.


## Running Tests
```bash
python manage.py test
```
