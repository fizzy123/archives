from django.core.management.base import BaseCommand, CommandError
from archives.functions import index_nodes

class Command(BaseCommand):
    help = 'indexes nodes'

    def handle(self, *args, **options):
        index_nodes()
