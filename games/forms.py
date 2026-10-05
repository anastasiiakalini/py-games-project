from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm

from games.models import (
    Developer,
    Country,
    Game,
    Genre,
)
from django.utils.text import slugify


class CountrySearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search country"}),
    )


class GenreSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search genre"}),
    )


class GameSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class GameCreationForm(ModelForm):
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), required=False)
    new_genre = forms.CharField(required=False, label="New genre")

    class Meta:
        model = Game
        fields = (
            "name",
            "genre",
            "developer",
            "description",
            "price",
        )

    def save(self, commit=True):
        game = super().save(commit=False)

        new_genre = self.cleaned_data.get("new_genre")

        if commit:
            game.save()
            self.save_m2m()

            if new_genre:
                genre, created = Genre.objects.get_or_create(
                    name=new_genre, defaults={"slug": slugify(new_genre)}
                )
                game.genre.add(genre)

        return game


class GameInformationUpdateForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "name",
            "genre",
            "developer",
            "description",
            "price",
        ]


class DeveloperSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class DeveloperCreationForm(UserCreationForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), required=False, empty_label="Choose a country"
    )

    new_country = forms.CharField(
        required=False,
        label="New country",
    )

    class Meta(UserCreationForm.Meta):
        model = Developer
        fields = UserCreationForm.Meta.fields + (
            "name",
            "country",
            "new_country",
            "website",
        )

    def clean(self):
        cleaned_data = super().clean()

        country = cleaned_data.get("country")
        new_country = cleaned_data.get("new_country")

        if country and new_country:
            raise forms.ValidationError(
                "Choose an existing country or enter a new one, not both."
            )

        if not country and not new_country:
            raise forms.ValidationError("Choose a country or enter a new one.")

        return cleaned_data

    def save(self, commit=True):
        developer = super().save(commit=False)

        new_country = self.cleaned_data.get("new_country")

        if new_country:
            country, created = Country.objects.get_or_create(name=new_country)
            developer.country = country

        if commit:
            developer.save()

        return developer


class DeveloperInformationUpdateForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), required=False, empty_label="Choose a country"
    )

    new_country = forms.CharField(required=False, label="New country")

    class Meta:
        model = Developer
        fields = (
            "name",
            "country",
            "new_country",
            "website",
        )

    def clean(self):
        cleaned_data = super().clean()

        country = cleaned_data.get("country")
        new_country = cleaned_data.get("new_country")

        if country and new_country:
            raise forms.ValidationError(
                "Choose an existing country or enter a new one, not both."
            )

        if not country and not new_country:
            raise forms.ValidationError("Choose a country or enter a new one.")

        return cleaned_data

    def save(self, commit=True):
        developer = super().save(commit=False)

        new_country = self.cleaned_data.get("new_country")

        if new_country:
            country, created = Country.objects.get_or_create(
                name=new_country, defaults={"slug": slugify(new_country)}
            )
            developer.country = country

        if commit:
            developer.save()

        return developer
