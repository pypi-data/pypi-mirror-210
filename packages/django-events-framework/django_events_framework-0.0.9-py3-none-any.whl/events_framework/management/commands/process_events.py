from django.core.management import BaseCommand

from ...manager import manager


class Command(BaseCommand):
    def handle(self, *args, **options):
        manager.process()
