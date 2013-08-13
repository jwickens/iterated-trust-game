from django.core.management.base import BaseCommand, CommandError
from game.models import Participant, Experiment, Treatment
import mturk

def approve_p(p):
	treat = p.treatment
	mtc = mturk.connect()
	result = {
		'already_approved':  0,
		'already_paid_bonus':  0,
		'approved':  0,
		'never_played':  0,
		'rejected':  0,
		'amnt': 0,
		'bonus': 0,
		}
	comm = (" If you have any questions please send them to jwickens@indiana.edu. "+
		    "Your reference number is "+str(p)+ '.')
	link = "http://perceptsconcepts.psych.indiana.edu/trustgame/mturk/"+str(p.workerId)
	
	if not p.base_pay:
		if p.passed_quiz:
		    msg = "Thank you for participating! "
		    if not p.treatment:
			    result['never_played'] = 1
			    msg += "It seems that you didn't have the chance to complete the experiment. You can still go to, " + link + '.'
			    msg += " You can still be paid bonuses of up to $7.20 by completing the experiment!"
		    msg+=comm
		    try:
			mtc.approve_assignment(p.assignmentId, msg)
			print "Approving " + str(p)
			result['approved'] = 1
			p.base_pay = 0.10
			p.save()
		    except:
			result['outstanding'] = 1
		else:
		    msg = "We're sorry, you did not complete the experimental pretest."
		    msg+= comm
		    try:
			mtc.reject_assignment(p.assignmentId,msg)
			print "Rejecting " + str(p)
			result['rejected'] = 1
			p.base_pay = 0.0
			p.save()
		    except:
			result['outstanding'] = 1

	else:
		result['already_approved'] = 1
	if not p.bonus_pay:
		if p.treatment and p.game_state == "completed":
	    	    amnt = p.experiment.earnings_multiplier * p.earnings
	    	    if amnt > 10:
	    		    print "This is too much!"
	    		    print "Not paying, " + str(amnt) + " to " + str(p)
	    	    else:
	    		    print 'Paying a bonus of, ' + str(amnt) + " to " + str(p)
			    result['bonus'] = 1
			    result['amnt'] = amnt
			    msg = "Thank you for your participation! "
			    msg += "You earned " + str(p.earnings) + " tokens in the experiment. "
			    msg += "Even if you feel like you didn't do well as you would have liked, "
			    msg += "most groups however never achieve high levels of trust. "
			    msg += "Your earnings thereby are also a small memento of your "
			    msg += "cooperative spirit. We certainly appreciate it as such. "
			    if not p.survey and p.machiv:
				msg += "Also do you know you haven't taken our exit survey? You can still take it at, " + link + '.'
			    msg += comm
			    mtc.grant_bonus(p.workerId, p.assignmentId, mturk.pay(amnt), msg)
			    p.bonus_pay = amnt
	    	    	    p.save()
	else:
		result['already_paid_bonus'] = 1
	return result


class Command(BaseCommand):
    args = ''
    help = ''
    def handle(self, *args, **kwargs):
	    parts = Participant.objects.filter(group='mturk')
	    print "Found " + str(len(parts)) + " mturk participants."
	    results = {}
	    for p in parts:
		    r = approve_p(p)
		    for k, x in r.items():
			    if k in results:
				    results[k]+=x
			    else:
				    results[k]=x
	    print results
					




    #def handle(self, *args, **options):
#	    if len(args) != 1:
#		    mturk.get_and_execute(approve_hit)
#	    else:
#		    approve_hit(args[0])


### DEPRECIATED
def approve_hit(hit_id):
	mtc = mturk.connect()
	assignments = mtc.get_assignments(hit_id)
	print "found " + str(len(assignments)) + " assignments."
	for assignment in assignments:
	        parts = Participant.objects.filter(workerId=assignment.WorkerId)
	        if len(parts)==0:
	    	    print "Could not find a participant with workerId, " + str(assignment.WorkerId)
	        elif len(parts)>1:
	    	    print "Found more than one record for workerId, " + str(assignment.WorkerId)
	    	    for p in parts:
	    		    str1 = "Started: " + str(p.started) + " | Ended: " + str(p.ended) + " | Passed Quiz: " + str(p.passed_quiz)
	    		    if p.treatment:
	    			    print str1 + "| Earnings: " + str(p.earnings)
	    		    else:
	    			    print str1 + ", NO TREATMENT"
	    	    ask = raw_input("Which one to use? ")
	    	    approve_p(parts[int(ask)])
	        else:
	    	    approve_p(parts[0])
