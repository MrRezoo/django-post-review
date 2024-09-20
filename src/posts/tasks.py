import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg
from django.db.models.functions import Coalesce, Round

from commons.messages.log_messges import LogMessages
from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post, PostStat, Rate

logger = logging.getLogger(__name__)


@shared_task
def update_post_stats_async(post_id, rate_id):
    post = Post.objects.get(id=post_id)
    rate = Rate.objects.get(id=rate_id)

    lock_key = RedisKeyTemplates.POST_STATS_LOCK.format(post_id=post_id)

    with cache.lock(lock_key, timeout=settings.CACHE_LOCK_TIMEOUT):
        stat, created = PostStat.objects.get_or_create(post=post)
        stat.average_rate = (stat.average_rate * stat.total_rates + rate.score) / (stat.total_rates + 1)
        stat.total_rates += 1
        stat.save()

        cache.set(RedisKeyTemplates.format_post_stats_key(post.id), {
            "average_rate": stat.average_rate,
            "total_rates": stat.total_rates
        }, settings.CACHE_TIMEOUT)


@shared_task
def update_stats_on_threshold_async(post_id, rate_id):
    post = Post.objects.get(id=post_id)
    rate = Rate.objects.get(id=rate_id)

    stat, created = PostStat.objects.get_or_create(post=post)
    stat.average_rate = (stat.average_rate * stat.total_rates + rate.score) / (stat.total_rates + 1)
    stat.total_rates += 1
    stat.save()


@shared_task
def update_post_stats_periodical(*, post_id: int):
    """
    Update the PostStat asynchronously while considering suspected rates.
    Scenarios:
        - If the difference between suspected rates and total rates is small,
          suspected rates are treated as normal rates.
        - Otherwise, suspected rates are treated as suspicious rates,
          and the average is calculated excluding them.
    """
    try:
        rates = Rate.objects.filter(post_id=post_id)
        total_rates = rates.count()
        suspected_rates_count = rates.filter(is_suspected=True).count()

        if total_rates == 0:
            average_rate = 0.0
        else:
            if suspected_rates_count < total_rates * settings.SUSPECTED_RATES_THRESHOLD:
                # Treat suspected rates as normal for averaging
                average_rate = (
                    rates.aggregate(
                        average=Coalesce(Round(Avg('score'), precision=1), 0.0)
                    )['average']
                )
            else:
                # Remove suspected rates from the average calculation
                average_rate = (
                    rates.exclude(is_suspected=True)
                    .aggregate(
                        average=Coalesce(Round(Avg('score'), precision=1), 0.0)
                    )['average']
                )

        with transaction.atomic():
            PostStat.objects.update_or_create(
                post_id=post_id,
                defaults={
                    'average_rate': average_rate,
                    'total_rates': total_rates
                }
            )
        cache.delete(RedisKeyTemplates.format_post_stats_key(post_id=post_id))
        logger.info(
            LogMessages.update_post_stats(post_id=post_id, average_rate=average_rate, total_rates=total_rates)
        )

    except Exception as e:
        logger.error(LogMessages.error_update_post_stats(post_id=post_id, error=e))