from django.core.management.base import BaseCommand, CommandError
import mturk


class Command(BaseCommand):
    args = 'HIT_ID'
    help = ''

    def handle(self, *args, **options):
	    mturk.create_hit()
