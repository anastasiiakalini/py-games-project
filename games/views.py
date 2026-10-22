from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from games.models import Game, Developer, Country, Genre

from games.forms import (
    CountrySearchForm,
    GenreSearchForm,
    GameSearchForm,
    GameCreationForm,
    GameInformationUpdateForm,
    DeveloperSearchForm,
    DeveloperCreationForm,
    DeveloperInformationUpdateForm,
)


@login_required
def index(request):
    """View function for the home page of the site."""

    num_games = Game.objects.count()
    num_developers = Developer.objects.count()
    num_countries = Country.objects.count()
    num_genres = Genre.objects.count()

    context = {
        "num_games": num_games,
        "num_developers": num_developers,
        "num_countries": num_countries,
        "num_genres": num_genres,
    }

    return render(request, "games/index.html", context=context)


class CountryListView(LoginRequiredMixin, generic.ListView):
    model = Country
    paginate_by = 5
    context_object_name = "country_list"
    template_name = "games/country_list.html"
    queryset = Country.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CountryListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = CountrySearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = CountrySearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(name__icontains=form.cleaned_data["name"])
        return self.queryset


class DeveloperByCountryListView(LoginRequiredMixin, generic.ListView):
    model = Developer
    template_name = "games/developer_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = DeveloperSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = (
            Developer.objects.filter(country__id=self.kwargs["pk"])
            .select_related("country")
            .order_by("name", "pk")
        )

        form = DeveloperSearchForm(self.request.GET)

        if form.is_valid():
            queryset = queryset.filter(name__icontains=form.cleaned_data["name"])

        return queryset


class DeveloperListView(LoginRequiredMixin, generic.ListView):
    model = Developer
    paginate_by = 5
    queryset = Developer.objects.order_by("name", "pk")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeveloperListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = DeveloperSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = DeveloperSearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(name__icontains=form.cleaned_data["name"])
        return self.queryset


class DeveloperDetailView(LoginRequiredMixin, generic.DetailView):
    model = Developer

    queryset = Developer.objects.select_related("country").prefetch_related(
        "games__genre"
    )


class DeveloperCreateView(generic.CreateView):
    model = Developer
    form_class = DeveloperCreationForm
    success_url = reverse_lazy("login")


class DeveloperUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Developer
    form_class = DeveloperInformationUpdateForm

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)

    def get_success_url(self):
        return reverse("games:developer-detail", kwargs={"pk": self.object.pk})


class DeveloperDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Developer
    success_url = reverse_lazy("games:developer-list")

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)


class GenreListView(LoginRequiredMixin, generic.ListView):
    model = Genre
    paginate_by = 5
    queryset = Genre.objects.order_by("name", "pk")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GenreListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = GenreSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = GenreSearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(name__icontains=form.cleaned_data["name"])
        return self.queryset


class GameListView(LoginRequiredMixin, generic.ListView):
    model = Game
    paginate_by = 5
    queryset = (
        Game.objects.select_related("developer")
        .prefetch_related("genre")
        .order_by("name", "pk")
    )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = GameSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = GameSearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(name__icontains=form.cleaned_data["name"])
        return self.queryset


class GameByGenreListView(LoginRequiredMixin, generic.ListView):
    model = Game
    template_name = "games/game_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")

        context["search_form"] = GameSearchForm(initial={"name": name})

        return context

    def get_queryset(self):
        queryset = (
            Game.objects.filter(genre__id=self.kwargs["pk"])
            .select_related("developer")
            .prefetch_related("genre")
            .order_by("name", "pk")
        )

        form = GameSearchForm(self.request.GET)

        if form.is_valid():
            queryset = queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class GameCreateView(LoginRequiredMixin, generic.CreateView):
    model = Game
    form_class = GameCreationForm

    def form_valid(self, form):
        form.instance.developer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("games:game-detail", kwargs={"pk": self.object.pk})


class GameUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Game
    form_class = GameInformationUpdateForm

    def get_success_url(self):
        return reverse("games:game-detail", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return super().get_queryset().filter(developer=self.request.user)


class GameDetailView(LoginRequiredMixin, generic.DetailView):
    model = Game
    queryset = Game.objects.select_related("developer").prefetch_related("genre")


class GameDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Game
    success_url = reverse_lazy("games:game-list")

    def get_queryset(self):
        return super().get_queryset().filter(developer=self.request.user)
