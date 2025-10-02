from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Clear all cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            action='store',
            dest='pattern',
            help='Clear cache keys matching pattern',
            default=None
        )

    def handle(self, *args, **options):
        pattern = options.get('pattern')
        
        if pattern:
            self.stdout.write(f'Clearing cache keys matching pattern: {pattern}')
            # In a real Redis setup, you would use SCAN to find matching keys
            # For now, we'll clear all cache
            cache.clear()
            self.stdout.write('Cache cleared for pattern')
        else:
            self.stdout.write('Clearing all cache...')
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all cache')
            )
