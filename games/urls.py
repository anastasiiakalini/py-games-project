from django.urls import path

from games.views import (
    index,
    CountryListView,
    DeveloperByCountryListView,
    DeveloperListView,
    DeveloperDetailView,
    DeveloperCreateView,
    DeveloperUpdateView,
    DeveloperDeleteView,
    GenreListView,
    GameListView,
    GameDetailView,
    GameCreateView,
    GameUpdateView,
    GameDeleteView,
    GameByGenreListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("countries/", CountryListView.as_view(), name="country-list"),
    path(
        "countries/<int:pk>/developer/",
        DeveloperByCountryListView.as_view(),
        name="developer-by-country",
    ),
    path("developers/", DeveloperListView.as_view(), name="developer-list"),
    path(
        "developers/<int:pk>/", DeveloperDetailView.as_view(), name="developer-detail"
    ),
    path("developers/create/", DeveloperCreateView.as_view(), name="developer-create"),
    path(
        "developers/<int:pk>/update/",
        DeveloperUpdateView.as_view(),
        name="developer-update",
    ),
    path(
        "developers/<int:pk>/delete/",
        DeveloperDeleteView.as_view(),
        name="developer-delete",
    ),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("genres/<int:pk>/games/", GameByGenreListView.as_view(), name="game-by-genre"),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("games/create/", GameCreateView.as_view(), name="game-create"),
    path(
        "games/<int:pk>/update/",
        GameUpdateView.as_view(),
        name="game-update",
    ),
    path(
        "games/<int:pk>/delete/",
        GameDeleteView.as_view(),
        name="game-delete",
    ),
]

app_name = "games"
