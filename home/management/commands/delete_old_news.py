from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from home.models import News


class Command(BaseCommand):
    help = "Delete news older than 1 year"

    def handle(self, *args, **kwargs):

        one_year_ago = now() - timedelta(days=180)

        old_news = News.objects.filter(
            published_date__lt=one_year_ago
        )

        count = old_news.count()

        old_news.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} old news articles."
            )
        )