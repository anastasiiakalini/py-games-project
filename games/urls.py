from django.urls import path

from .views import (
    index,
    CountryListView,
    CountryCreateView,
    CountryUpdateView,
    # CountryDeleteView,
    DeveloperByCountryListView,
    DeveloperListView,
    DeveloperDetailView,
    DeveloperCreateView,
    DeveloperUpdateView,
    # DeveloperDeleteView,
    GenreListView,
    GameListView,
    GameDetailView,
    GameCreateView,
    GameUpdateView,
    GameByGenreListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("countries/", CountryListView.as_view(), name="country-list"),
    path("countries/create/", CountryCreateView.as_view(), name="country-create"),
    path(
        "countries/<int:pk>/update/",
        CountryUpdateView.as_view(),
        name="country-update",
    ),
    path(
        "countries/<slug:slug>/developer/",
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
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path(
        "genres/<slug:slug>/games/", GameByGenreListView.as_view(), name="game-by-genre"
    ),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("games/create/", GameCreateView.as_view(), name="game-create"),
    path(
        "games/<int:pk>/update/",
        GameUpdateView.as_view(),
        name="game-update",
    ),
]

app_name = "games"
