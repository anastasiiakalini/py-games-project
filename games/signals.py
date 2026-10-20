from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from .models import Game, Genre, Developer, Country

# GAME SIGNALS


@receiver(pre_delete, sender=Game)
def remember_game_genres(sender, instance, **kwargs):
    instance.genre_ids = list(instance.genre.values_list("id", flat=True))


@receiver(post_delete, sender=Game)
def delete_unused_genres(sender, instance, **kwargs):
    Genre.objects.filter(id__in=instance.genre_ids, games__isnull=True).delete()


# DEVELOPER SIGNALS


@receiver(pre_delete, sender=Developer)
def remember_developer_data(sender, instance, **kwargs):
    instance.country_id_to_check = instance.country_id


@receiver(post_delete, sender=Developer)
def delete_unused_data(sender, instance, **kwargs):
    Country.objects.filter(
        id=instance.country_id_to_check, developers__isnull=True
    ).delete()
