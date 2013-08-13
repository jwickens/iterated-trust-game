from django.core.management.base import BaseCommand, CommandError
from game.models import Participant, Experiment, Treatment
import mturk


class Command(BaseCommand):
    args = 'HIT_ID'
    help = ''

    def handle(self, *args, **options):
	    mtc = mturk.connect()
	    parts = Participant.objects.filter(group='mturk')
	    for p in parts:
		    treat = p.treatment
		    if not p.base_pay:
			    if p.passed_quiz:
				    print "Approving " + str(p)
				    p.base_pay = 0.10
				    p.save()
				    mtc.approve_assignment(p.assignmentId, "Thank you for participating!")
			    else:
				    print "Rejecting " + str(p)
				    mtc.reject_assignment(p.assignmentId,
				    "We're sorry, you did not complete the experimental pretest. Send all questions to jwickens@indiana.edu. "+
				    "Include the reference, "+str(p)+ '.')
		    else:
			    print str(p) + " has already been approved."
		    if not p.bonus_pay:
			    if p.ended:
				    amnt = p.experiment.earnings_multiplier * p.earnings
				    print 'Paying a bonus of, ' + amnt + " to " + str(p)
				    p.bonus_pay = amnt
				    p.save()
				    mtc.grant_bonus(p.workerId, p.assignmentId, pay(amnt), 
				    "Thank you for your participation. You earned, " + str(p.earnings) + " tokens in the "+
				    "experiment. Send all questions to jwickens@indiana.edu. Include the reference, " + str(p)+ '.')
		    else:
			    print str(p) + " has already had their bonus paid."
			
			
