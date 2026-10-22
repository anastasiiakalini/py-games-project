from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from games.models import Country, Genre, Developer, Game

from games.forms import DeveloperCreationForm, GameCreationForm


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


class GameSignalTests(TestCase):

    def setUp(self):
        self.country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="CD Projekt",
            country=self.country,
            website="https://example.com",
        )

    def test_genre_is_not_deleted_if_other_games_use_it(self):
        genre = Genre.objects.create(name="RPG")

        game1 = Game.objects.create(
            name="Cyberpunk",
            developer=self.developer,
            description="Test",
            price=50,
        )

        game2 = Game.objects.create(
            name="The Witcher",
            developer=self.developer,
            description="Test",
            price=30,
        )

        game1.genre.add(genre)
        game2.genre.add(genre)

        game1.delete()

        self.assertTrue(Genre.objects.filter(pk=genre.pk).exists())

    def test_genre_is_deleted_if_it_is_empty(self):
        genre = Genre.objects.create(name="RPG")

        game = Game.objects.create(
            name="Cyberpunk",
            developer=self.developer,
            description="Test",
            price=50,
        )

        game.genre.add(genre)

        game.delete()

        self.assertFalse(Genre.objects.filter(pk=genre.pk).exists())


class DeveloperSignalTests(TestCase):

    def test_country_is_not_deleted_if_other_developer_uses_it(self):
        country = Country.objects.create(name="Ukraine")

        developer_1 = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="CD Projekt",
            country=country,
            website="https://example_1.com",
        )

        developer_2 = Developer.objects.create_user(
            username="developer2",
            password="testpassword1234",
            name="GSC Game World",
            country=country,
            website="https://example_2.com",
        )

        developer_1.delete()

        self.assertTrue(Country.objects.filter(pk=country.pk).exists())

    def test_country_is_deleted_when_last_developer_is_deleted(self):
        country = Country.objects.create(name="Ukraine")

        developer = Developer.objects.create_user(
            username="developer",
            password="testpassword123",
            name="CD Projekt",
            country=country,
            website="https://example.com",
        )

        developer.delete()

        self.assertFalse(Country.objects.filter(pk=country.pk).exists())

    def test_unrelated_country_is_not_deleted(self):
        country_1 = Country.objects.create(name="Ukraine")
        country_2 = Country.objects.create(name="Poland")

        developer = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="CD Projekt",
            country=country_1,
            website="https://example.com",
        )

        developer.delete()

        self.assertTrue(Country.objects.filter(pk=country_2.pk).exists())


class GameAccessTests(TestCase):
    def setUp(self):
        country = Country.objects.create(name="Poland")

        self.owner = Developer.objects.create_user(
            username="owner",
            password="testpassword123",
            name="Game Owner",
            country=country,
            website="https://example.com",
        )

        self.other_developer = Developer.objects.create_user(
            username="other",
            password="testpassword123",
            name="Other Developer",
            country=country,
            website="https://example.org",
        )

        self.genre = Genre.objects.create(name="Adventure")

        self.game = Game.objects.create(
            name="Original Game",
            description="Original description",
            price="20.00",
            developer=self.owner,
        )

        self.game.genre.add(self.genre)

        self.client.force_login(self.other_developer)

    def test_cannot_update_another_developers_game(self):
        response = self.client.post(
            reverse("games:game-update", args=[self.game.pk]),
            data={
                "name": "Changed Game",
                "genre": [self.genre.pk],
                "description": "Changed description",
                "price": "10.00",
            },
        )

        self.assertEqual(response.status_code, 404)

        self.game.refresh_from_db()
        self.assertEqual(self.game.name, "Original Game")

    def test_cannot_delete_another_developers_game(self):
        response = self.client.post(reverse("games:game-delete", args=[self.game.pk]))

        self.assertEqual(response.status_code, 404)

        self.assertTrue(Game.objects.filter(pk=self.game.pk).exists())


class GameCreationTests(TestCase):
    def setUp(self):
        country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="game_creator",
            password="testpassword123",
            name="Game Creator",
            country=country,
            website="https://example.com",
        )

        self.genre = Genre.objects.create(name="RPG")

    def test_new_game_belongs_to_logged_in_developer(self):
        self.client.force_login(self.developer)

        response = self.client.post(
            reverse("games:game-create"),
            data={
                "name": "New Game",
                "genre": [self.genre.pk],
                "new_genre": "",
                "description": "A game description",
                "price": "49.99",
            },
        )

        self.assertEqual(response.status_code, 302)

        game = Game.objects.get(name="New Game")
        self.assertEqual(game.developer, self.developer)

    def test_new_genre_is_created_with_game(self):
        form = GameCreationForm(
            data={
                "name": "Strategy Game",
                "genre": [],
                "new_genre": "Strategy",
                "description": "A game with a new genre",
                "price": "29.99",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        form.instance.developer = self.developer
        game = form.save()

        self.assertTrue(Genre.objects.filter(name="Strategy").exists())

        self.assertTrue(game.genre.filter(name="Strategy").exists())

    def test_game_form_rejects_missing_genre(self):
        form = GameCreationForm(
            data={
                "name": "Game Without Genre",
                "genre": [],
                "new_genre": "",
                "description": "A game without genres",
                "price": "19.99",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "You must select at least one genre or enter a new one.",
            form.non_field_errors(),
        )


class DeveloperProfileTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Poland")

        self.owner = Developer.objects.create_user(
            username="profile_owner",
            password="testpassword123",
            name="Original Studio",
            country=self.country,
            website="https://original.example.com",
        )
        self.other_developer = Developer.objects.create_user(
            username="another_developer",
            password="testpassword123",
            name="Another Studio",
            country=self.country,
            website="https://another.example.com",
        )
        self.client.force_login(self.owner)

    def test_owner_can_update_profile(self):
        response = self.client.post(
            reverse("games:developer-update", args=[self.owner.pk]),
            data={
                "name": "Updated Studio",
                "country": self.country.pk,
                "new_country": "",
                "website": "https://updated.example.com",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.name, "Updated Studio")
        self.assertEqual(self.owner.website, "https://updated.example.com")

    def test_owner_can_delete_profile(self):
        owner_id = self.owner.pk
        response = self.client.post(reverse("games:developer-delete", args=[owner_id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Developer.objects.filter(pk=owner_id).exists())

    def test_cannot_update_another_profile(self):
        response = self.client.post(
            reverse("games:developer-update", args=[self.other_developer.pk]),
            data={
                "name": "Wrong Update",
                "country": self.country.pk,
                "new_country": "",
                "website": "https://changed.example.com",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.other_developer.refresh_from_db()
        self.assertEqual(self.other_developer.name, "Another Studio")

    def test_cannot_delete_another_profile(self):
        response = self.client.post(
            reverse("games:developer-delete", args=[self.other_developer.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Developer.objects.filter(pk=self.other_developer.pk).exists())


class GameOwnerActionsTests(TestCase):
    def setUp(self):
        country = Country.objects.create(name="Poland")
        self.developer = Developer.objects.create_user(
            username="game_owner",
            password="testpassword123",
            name="Game Studio",
            country=country,
            website="https://studio.example.com",
        )
        self.genre = Genre.objects.create(name="RPG")
        self.game = Game.objects.create(
            name="Original Game",
            description="Original description",
            price="20.00",
            developer=self.developer,
        )
        self.game.genre.add(self.genre)
        self.client.force_login(self.developer)

    def test_owner_can_update_game(self):
        response = self.client.post(
            reverse("games:game-update", args=[self.game.pk]),
            data={
                "name": "Updated Game",
                "genre": [self.genre.pk],
                "description": "Updated description",
                "price": "35.00",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.name, "Updated Game")
        self.assertEqual(self.game.description, "Updated description")

    def test_owner_can_delete_game(self):
        game_id = self.game.pk
        response = self.client.post(reverse("games:game-delete", args=[game_id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Game.objects.filter(pk=game_id).exists())


class CatalogFiltersTests(TestCase):
    def setUp(self):
        self.poland = Country.objects.create(name="Poland")
        self.ukraine = Country.objects.create(name="Ukraine")
        self.polish_developer = Developer.objects.create_user(
            username="polish_studio",
            password="testpassword123",
            name="Polish Studio",
            country=self.poland,
            website="https://polish.example.com",
        )
        self.ukrainian_developer = Developer.objects.create_user(
            username="ukrainian_studio",
            password="testpassword123",
            name="Ukrainian Studio",
            country=self.ukraine,
            website="https://ukrainian.example.com",
        )
        self.rpg = Genre.objects.create(name="RPG")
        self.strategy = Genre.objects.create(name="Strategy")
        self.rpg_game = Game.objects.create(
            name="RPG Game",
            description="Role-playing game",
            price="25.00",
            developer=self.polish_developer,
        )
        self.strategy_game = Game.objects.create(
            name="Strategy Game",
            description="Strategy game",
            price="30.00",
            developer=self.ukrainian_developer,
        )
        self.rpg_game.genre.add(self.rpg)
        self.strategy_game.genre.add(self.strategy)
        self.client.force_login(self.polish_developer)

    def test_games_can_be_filtered_by_genre(self):
        response = self.client.get(reverse("games:game-by-genre", args=[self.rpg.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["object_list"]),
            [self.rpg_game],
        )

    def test_developers_can_be_filtered_by_country(self):
        response = self.client.get(
            reverse("games:developer-by-country", args=[self.poland.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["object_list"]),
            [self.polish_developer],
        )


class GamePaginationTests(TestCase):
    def setUp(self):
        country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="pagination_owner",
            password="testpassword123",
            name="Studio",
            country=country,
            website="https://example.com",
        )
        for number in range(7):
            Game.objects.create(
                name=f"Game {number}",
                description="For pagination testing",
                price="10.00",
                developer=self.developer,
            )
        self.client.force_login(self.developer)

    def test_game_list_has_five_items_on_first_page(self):
        response = self.client.get(reverse("games:game-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["object_list"]), 5)

    def test_second_page_has_two_items(self):
        response = self.client.get(reverse("games:game-list"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 2)
        self.assertEqual(response.context["page_obj"].number, 2)


class AuthenticationAndInvalidIdTests(TestCase):
    def setUp(self):
        country = Country.objects.create(name="Poland")
        self.developer = Developer.objects.create_user(
            username="auth_studio",
            password="testpassword123",
            name="Auth Studio",
            country=country,
            website="https://example.com",
        )
        self.game = Game.objects.create(
            name="Protected Game",
            description="Test",
            price="15.00",
            developer=self.developer,
        )

    def test_anonymous_user_is_redirected_from_games(self):
        response = self.client.get(reverse("games:game-list"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_anonymous_user_cannot_create_game(self):
        response = self.client.post(
            reverse("games:game-create"),
            data={
                "name": "Unauthorized Game",
                "description": "Test",
                "price": "10.00",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Game.objects.filter(name="Unauthorized Game").exists())

    def test_nonexistent_game_returns_404(self):
        self.client.force_login(self.developer)
        response = self.client.get(reverse("games:game-detail", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_nonexistent_developer_returns_404(self):
        self.client.force_login(self.developer)
        response = self.client.get(reverse("games:developer-detail", args=[999999]))

        self.assertEqual(response.status_code, 404)


class ModelConstraintsTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Poland")

        self.developer = Developer.objects.create_user(
            username="model_studio",
            password="testpassword123",
            name="Model Studio",
            country=self.country,
            website="https://example.com",
        )

    def test_negative_game_price_is_invalid(self):
        game = Game(
            name="Invalid Price Game",
            description="Test",
            price="-5.00",
            developer=self.developer,
        )

        with self.assertRaises(ValidationError) as error:
            game.full_clean()

        self.assertIn("price", error.exception.message_dict)

    def test_duplicate_game_name_is_invalid(self):
        Game.objects.create(
            name="Same Game",
            description="First",
            price="10.00",
            developer=self.developer,
        )
        duplicate_game = Game(
            name="Same Game",
            description="Second",
            price="20.00",
            developer=self.developer,
        )

        with self.assertRaises(ValidationError) as error:
            duplicate_game.full_clean()

        self.assertIn("name", error.exception.message_dict)

    def test_duplicate_country_name_is_invalid(self):
        duplicate_country = Country(name="Poland")

        with self.assertRaises(ValidationError) as error:
            duplicate_country.full_clean()


class DuplicatePreventionTests(TestCase):

    def setUp(self):
        self.country = Country.objects.create(name="Ukraine")

        self.developer = Developer.objects.create_user(
            username="developer1",
            password="testpassword123",
            name="Test Developer",
            country=self.country,
            website="https://example.com",
        )

        self.genre = Genre.objects.create(name="RPG")

    def test_country_is_not_duplicated(self):
        form = DeveloperCreationForm(
            data={
                "username": "developer2",
                "password1": "StrongPass_12345",
                "password2": "StrongPass_12345",
                "name": "Another Developer",
                "country": "",
                "new_country": " UKRAINE ",
                "website": "https://example.com",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        developer = form.save()

        self.assertEqual(developer.country, self.country)
        self.assertEqual(Country.objects.count(), 1)

    def test_genre_is_not_duplicated(self):
        form = GameCreationForm(
            data={
                "name": "New Game",
                "genre": [],
                "new_genre": " rpg ",
                "description": "Test description",
                "price": "19.99",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        form.instance.developer = self.developer
        game = form.save()

        self.assertTrue(game.genre.filter(pk=self.genre.pk).exists())

        self.assertEqual(Genre.objects.count(), 1)
