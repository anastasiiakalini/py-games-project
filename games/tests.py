from django.test import TestCase
from django.urls import reverse

from .models import Country, Genre, Developer, Game
from .forms import DeveloperCreationForm


class CountryModelTests(TestCase):
    def test_country_slug_is_created_automatically(self):
        country = Country.objects.create(name="United States")

        self.assertEqual(country.slug, "united-states")


class GenreModelTests(TestCase):
    def test_genre_slug_is_created_automatically(self):
        genre = Genre.objects.create(name="Action Games")

        self.assertEqual(genre.slug, "action-games")


class GameModelTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="CD Projekt",
            country=self.country,
            website="https://example.com",
        )

        self.genre = Genre.objects.create(name="RPG")

        self.game = Game.objects.create(
            name="Cyberpunk 2077",
            description="Test description",
            price=59.99,
            developer=self.developer,
        )

        self.game.genre.add(self.genre)

    def test_game_name(self):
        self.assertEqual(self.game.name, "Cyberpunk 2077")

    def test_game_developer(self):
        self.assertEqual(self.game.developer, self.developer)

    def test_game_genre(self):
        self.assertIn(self.genre, self.game.genre.all())


class GameListViewTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="Developer",
            country=self.country,
            website="https://example.com",
        )

        Game.objects.create(
            name="Cyberpunk",
            description="Test",
            price=20,
            developer=self.developer,
        )

        Game.objects.create(
            name="The Witcher",
            description="Test",
            price=20,
            developer=self.developer,
        )

        self.client.force_login(self.developer)

    def test_search_game_by_name(self):
        response = self.client.get(reverse("games:game-list"), {"name": "Cyber"})

        self.assertContains(response, "Cyberpunk")

        self.assertNotContains(response, "The Witcher")


class AuthenticationTests(TestCase):
    def test_game_list_requires_login(self):
        response = self.client.get(reverse("games:game-list"))

        self.assertEqual(response.status_code, 302)


class DeveloperCreationFormTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Poland")

    def test_form_valid_with_existing_country(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer1",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "CD Projekt",
                "country": self.country.pk,
                "new_country": "",
                "website": "https://example.com",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_valid_with_new_country(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer2",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "New Developer",
                "country": "",
                "new_country": "Germany",
                "website": "https://example.com",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_invalid_with_existing_and_new_country(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer3",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "Developer",
                "country": self.country.pk,
                "new_country": "Germany",
                "website": "https://example.com",
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_invalid_without_country(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer4",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "Developer",
                "country": "",
                "new_country": "",
                "website": "https://example.com",
            }
        )

        self.assertFalse(form.is_valid())

    def test_save_creates_new_country(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer5",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "New Developer",
                "country": "",
                "new_country": "Germany",
                "website": "https://example.com",
            }
        )

        self.assertTrue(form.is_valid())

        developer = form.save()

        self.assertTrue(Country.objects.filter(name="Germany").exists())

        self.assertEqual(developer.country.name, "Germany")

        self.assertEqual(Country.objects.count(), 2)
