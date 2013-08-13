from django.core.management.base import BaseCommand, CommandError
import mturk
class Command(BaseCommand):
    args = 'HIT_ID'
    help = ''
    def handle(self, *args, **options):
	    method = mturk.connect().expire_hit
	    if len(args) != 1:
		    mturk.get_and_execute(method)
	    else:
		    method(args[0])
