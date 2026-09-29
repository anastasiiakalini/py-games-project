from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Genre, Game, Developer, Country


@admin.register(Developer)
class DeveloperAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        "country",
        "website",
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "name",
                        "country",
                        "website",
                    )
                },
            ),
        )
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "name",
                        "country",
                        "website",
                    )
                },
            ),
        )
    )


admin.site.register(Genre)
admin.site.register(Country)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("developer",)
