from django.core.management.base import BaseCommand, CommandError
from game.models import Participant, Experiment, Treatment
import csv

def print_table(matrix):
	s = [[str(e) for e in row] for row in matrix]
	lens = [len(max(col, key=len)) for col in zip(*s)]
	fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print '\n'.join(table)

def create_relationship_id(p1, p2):
	ps = list(p1.treatment.participants)
	position1 = ps.index(p1)
	position2 = ps.index(p2)
	if (position1 == 0 and position2 == 1):
		return 1
	elif(position1 == 1 and position2 == 0):
		return 2
	elif (position1 == 1 and position2 == 2):
		return 3
	elif (position1 == 2 and position2 == 1):
		return 4
	elif (position1 == 2 and position2 == 0):
		return 5
	else:
		return 6

def get_relationship_id(turn, returner_id):
	return (turn.treatment.pk)**2 + create_relationship_id(turn.get_participant(turn.transferer), turn.get_participant(returner_id))

def get_crelationship_id(turn, returner_id):
	return (turn.condition.pk)**2 + create_relationship_id(turn.get_participant(turn.transferer), turn.get_participant(returner_id))




class Command(BaseCommand):
    args = 'experimental group'
    help = ''

    def handle(self, *args, **options):
	    if len(args) > 0:
		    group = args[0]
	    else:
		    group = 'mturk'
	    print "Data for " + group
	    exp = getattr(Experiment, group)()

	    print "Treatments:"
	    print exp.count_treatments()

	    print "Completed Treatments:"
	    print exp.count_treatments(valid=True)

	    print "Treatments with valid Participants:"
	    print exp.count_treatments(valid=True, valid_participants=True)

	    print "Ouputting to File turn_relations.csv Transfer Return Pairs in valid Treatments..."
	    matrix = [[
		    'turn',
		    'condition',
		    'treatment',
		    'treatment_label',
		    'transfer',
		    'return',
		    'default_transfer',
		    'default_return',
		    'earnings_transferrer',
		    'earnings_returner',
		    'total_earnings_transferrer',
		    'total_earnings_returner',
		    'link_condition',
		    'info_condition',
		    'total_time_transferrer',
		    'total_time_returner',
		    'workerId_transferrer',
		    'workerId_returner',
		    'machiv_transferrer',
		    'machiv_returner',
		    'age_transferrer',
		    'age_returner',
		    'pretest_tries_transferrer',
		    'pretest_tries_returner',
		    'prev_exp_transferrer',
		    'prev_exp_returner',
		    'clarity_transferrer',
		    'clarity_returner',
		    'tech_difficulties_transferrer',
		    'tech_difficulties_returner',
		    'educ_transferrer',
		    'educ_returner',
		    'gender_transferrer',
		    'gender_returner',
		    'lagged_transfer',
		    'lagged_avg_return',
		    'relationship',
		    'crelationship',
		    'conditionid',

	    ]]
	    for treat in exp.treatments.filter(valid=True):
		    for condition in treat.conditions.all():
			    for turn in condition.turns.all():
				    for i in range(3):
					    if turn.transferer != i:
						    matrix.append( [
								    turn.num,
								    condition.num,
								    str(treat.pk),
								    str(treat.label),
								    getattr(turn, 'transfer'+str(i)),
								    getattr(turn, 'return'+str(i)),
								    getattr(turn, 'default'+str(turn.transferer)),
								    getattr(turn, 'default'+str(i)),
								    getattr(turn, 'earnings'+str(turn.transferer)),
								    getattr(turn, 'earnings'+str(i)),
								    turn.get_participant(turn.transferer).earnings,
								    turn.get_participant(i).earnings,
								    str(condition.link_condition),
								    str(condition.info_condition),
								    turn.get_participant(turn.transferer).total_time,
								    turn.get_participant(i).total_time,
								    turn.get_participant(turn.transferer).workerId,
								    turn.get_participant(i).workerId,
								    turn.get_participant(turn.transferer).machiv_score,
								    turn.get_participant(i).machiv_score,
								    turn.get_participant(turn.transferer).consent_age,
								    turn.get_participant(i).consent_age,
								    turn.get_participant(turn.transferer).pretest_tries,
								    turn.get_participant(i).pretest_tries,
								    turn.get_participant(turn.transferer).get_survey('prev_exp'),
								    turn.get_participant(i).get_survey('prev_exp'),
								    turn.get_participant(turn.transferer).get_survey('clarity'),
								    turn.get_participant(i).get_survey('clarity'),
								    turn.get_participant(turn.transferer).get_survey('tech'),
								    turn.get_participant(i).get_survey('tech'),
								    turn.get_participant(turn.transferer).get_survey('educ'),
								    turn.get_participant(i).get_survey('educ'),
								    turn.get_participant(turn.transferer).get_survey('gender'),
								    turn.get_participant(i).get_survey('gender'),
								    turn.get_lagged_var('transfer'+str(turn.transferer)),
								    turn.get_lagged_var('avg_return'),
								    get_relationship_id(turn,i),
								    get_crelationship_id(turn,i),
								    condition.pk

								   ] )

	    with open('turn_relations.csv', 'wb') as f:
		    writer = csv.writer(f)
		    writer.writerows(matrix)

