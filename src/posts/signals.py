from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Rate


@receiver(post_save, sender=Rate)
def update_post_stats_signal(sender, instance, **kwargs):
    from posts.services.commands import update_or_create_stat
    update_or_create_stat(post_id=instance.post, new_score=instance.score)
