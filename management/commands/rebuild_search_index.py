from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.management.commands.search_index import Command as SearchIndexCommand
from search.documents import ProductDocument, CategoryDocument


class Command(BaseCommand):
    help = 'Rebuild Elasticsearch search index'

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            action='store',
            dest='models',
            help='Specify which models to index',
            default=''
        )
        parser.add_argument(
            '--parallel',
            action='store_true',
            dest='parallel',
            help='Run indexing in parallel',
            default=False
        )

    def handle(self, *args, **options):
        self.stdout.write('Rebuilding search index...')
        
        # Delete existing indices
        self.stdout.write('Deleting existing indices...')
        ProductDocument._index.delete(ignore=[404])
        CategoryDocument._index.delete(ignore=[404])
        
        # Create new indices
        self.stdout.write('Creating new indices...')
        ProductDocument._index.create()
        CategoryDocument._index.create()
        
        # Populate indices
        self.stdout.write('Populating indices...')
        ProductDocument().update()
        CategoryDocument().update()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully rebuilt search index')
        )
