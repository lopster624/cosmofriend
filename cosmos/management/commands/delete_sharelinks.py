from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from cosmos.models import ShareLink


class Command(BaseCommand):
    help = 'Удаляет все временные ссылки, время жизни которых закончилось'

    def handle(self, *args, **kwargs):
        links = ShareLink.objects.filter(date_of_die__lte=datetime.now())
        if not links:
            self.stdout.write(f'Нет устаревших ссылок')
        for link in links:
            link.delete()
            self.stdout.write(f'Была удалена ссылка с токеном {link.token}')
