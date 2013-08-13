from django.core.management.base import NoArgsCommand, CommandError
from game.models import Participant, Experiment, Treatment


class Command(NoArgsCommand):
    args = 'None'
    help = ''

    def handle(self, *args, **options):
	    valid_treats = Treatment.objects.filter(valid=True).filter(valid_participants=True)
	    #valid_treats = Treatment.objects.all()
	    for t in valid_treats:
		print t
		participants = t.participants
		for p in participants:
			print str(p) + ' earned, ' + str(p.earnings)
