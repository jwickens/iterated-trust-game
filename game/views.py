from django.shortcuts import render, redirect
from django.http import HttpResponse
from form import ConsentForm, TransferForm, ReturnForm, QuizForm
from exitsurvey import SurveyForm, MACHIVForm, BIG5Form
from random import choice
from game.models import Experiment, Participant, Turn
from datetime import datetime
from django.utils.timezone import utc
import csv

def nav(step, bonus=None, experiment=None, p=None):
	navsteps = ['Preview', 'Consent', 'Instructions', 'Sandbox',	'Pretest', 'Waiting Room', 'Experiment', 'Exit Survey']
	navtime  = [ '',	'3 min.',	'5 min.', '5 min.',	'5 min.',	'10 min.',	'20 min.',	'7 min.']
	reward	 = [ 'Payments:',	'',		'',	 '',		'HIT approved $0.10',	'',		'',	'']
	r = None
	if p:
		grp = p.group
		experiment = p.experiment
	else:
		grp = experiment.group
	if grp != 'mturk' and grp != 'mturk-fake':
		if step > 1:
			step -= 1
		del navsteps[1]
		del navtime[1]
	else:
		if step>=8:
			reward[6]='You earned $%.2f' % (experiment.earnings_multiplier*p.earnings)
		else:
			reward[6]='Up to $%.2f Avg. $1.50' % (experiment.earnings_multiplier*3600)
		r = reward

	context = {	'navsteps': navsteps,
			'navtime': navtime,
			'reward': r,
			'stage_num': step,
		}
	return context


def curb(experiment):
	context = {'context': Experiment.curb_treatment().participants[0].diagram_context}
	context.update(nav(1,experiment=experiment))
	return context
		
##### VERIFICATION ######
def find_p(pk):
	p = Participant.objects.filter(pk=pk)
	if len(p) == 1:
		return {'participant': p[0]}
	else:
		return {'error': "Could not find the participant_id stored in your browser session." }


def find_worker(workerId, assignmentId=None):
	parts = Participant.objects.filter(workerId=workerId)
	errors = []
	if len(parts) > 1:
		errors.append( "It appears you have already initialized the experiment. Got more than one entry with your workerId.")
	elif len(parts) == 1:
		if assignmentId and parts[0].assignmentId != assignmentId:
			p = parts[0]
			errors.append("It appears you already participated in this experiment.")
			errors.append("Got a previous record with a different assignmentId: " + p.assignmentId )
			errors.append("Got a previous record with a different hitId: " + p.hitId )
		return {'participant': parts[0], 'errors': errors }
	else:
		return {'errors': errors} 

def verify_records(pk=None, workerId=None, assignmentId=None):
	errors = []
	pwrk = None
	ppk = None
	if bool(workerId):
		parg = find_worker(workerId, assignmentId)
		if 'participant' in parg:
			pwrk = parg['participant'] # Participant by workerId
		else:
			pwrk = None
		if 'errors' in parg:
			errors+=parg['errors']
	if pk:
		parg = find_p(pk)
		if 'participant' in parg:
			ppk = parg['participant'] # Participant by pk
		else:
			ppk = None
		if 'error' in parg:
			errors.append(parg['error'])
	if pwrk and pk:
		if pwrk.pk != pk:
			print "Worker with workerId, " + str(workerId) + " has tried to hack the cookie"
			errors.append("There is something fishy about your cookies.")
	if ppk and bool(workerId and assignmentId):
		if ppk.workerId != workerId:
			print "Worker with workerId, " + str(workerId) + " has tried to enter twice with different mturk accounts"
			errors.append("It seems you have started this HIT already on another account.")
		if ppk.assignmentId != assignmentId:
			errors.append("You have started this HIT already in another assignment. You can only participate in this experiment once.")
	if ppk:
		return {'participant': ppk, 'errors': errors }
	elif pwrk:
		return {'participant': pwrk, 'errors': errors }
	else:
		if len(errors) > 0:
			return {'errors': errors}
		else:
			return None
	
def get_max_stage(p):
	if bool(p.survey and p.machiv):
		return 'end'
	elif p.ended:
		return 'survey'
	elif p.treatment:
		if p.game_state == 'completed':
			return 'survey'
		else:
			return 'game'
	elif p.passed_quiz:
		return 'start'
	elif p.consent:
		return 'pretest'
	elif p.started:
		return 'consent'
	elif bool(p.hitId and p.workerId and p.assignmentId):
		return 'mturk'
	else:
		return 'portal'

##### Wrappers to return a response or participant or none ######
def get_worker_records(request, pk=None, workerId=None, assignmentId=None):
	records = verify_records(pk, workerId, assignmentId)
	if records:
		errors = records['errors']
		p = None
		if 'participant' in records:
			p = records['participant']
		if len(errors) > 0:
			msg = "<p>There were problem(s) with your record:</p><ul>"
			for e in errors:
				msg += '<li>' + e + '</li>'
			msg += '</ul>'
			if p:
				return {'error': error(request, msg, p)}
			else:
				return {'error': error(request, msg)}
		else:
			if p:
				return {'stage': get_max_stage(p), 'participant': p}
			else:
				return None
	else:
		return None

def get_worker(request, workerId=None):
	if not workerId:
		workerId = request.GET.get(u'workerId' )
	assignmentId = request.GET.get(u'assignmentId')
	part_num = request.session.get('part_num')
	return get_worker_records(request, part_num, workerId, assignmentId)

def check_records(records, stage=None,noRedirect=False): # compares to current stage, ie instructions, consent, etc.
	if 'error' in records:
		return {'redirect': records['error']}
	elif not noRedirect and 'stage' in records and stage and records['stage'] != stage: # is stage supplied, see if p is in the stage he should be, redirect him if not
		return {'redirect': redirect(records['stage'])}
	else:
		return {'participant': records['participant']}

def check_init(request, stage=None, workerId=None):
	records = get_worker(request, workerId)
	if records:
		return check_records(records, stage)
	else:
		return {'redirect': error(request,
		'The experiment has not been initialized correctly or your cookie was lost. Please access the experiment again, making sure to accept the HIT, '+
		'and ensure that cookies are enabled.')}

##### ENTRY POINTS ######
def portal(request):
	#Mturk
	p = None
	records = get_worker(request)
	if records:
		verified = check_records(records,'portal',noRedirect=True)
		if 'redirect' in verified:
			return verified['redirect']
		else:
			p = verified['participant']

	hitId = request.GET.get(u'hitId')
	assignmentId = request.GET.get(u'assignmentId')
	workerId = request.GET.get(u'workerId' )
	turkSubmitTo = request.GET.get(u'turkSubmitTo' )
	if bool( hitId and assignmentId and workerId):
		if not p:
			p = Participant.create(group='mturk',hitId=hitId,assignmentId=assignmentId,workerId=workerId,turkSubmitTo=turkSubmitTo)
			p.save()
			request.session['part_num'] = p.id
		return render(request, "mturk_form.html", {'p':p, })
	else:
		context = curb(Experiment.mturk())
		context['disabled'] = True
		return render(request, "portal.html", context)

def mturk(request, workerId):
	records = check_init(request, 'mturk')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	now = datetime.utcnow().replace(tzinfo=utc)
	p.started = now
	p.save()
	return render(request, "portal.html", curb(Experiment.mturk()))


def coop(request):
	now = datetime.utcnow().replace(tzinfo=utc)
	p = Participant(group='coop', started=now)
	p.save()
	request.session['part_num'] = p.id
	return render(request, "coop.html", curb(Experiment.coop()))
##############################

def consent(request):
	records = check_init(request, 'consent')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	form = ConsentForm()
	if request.method == "POST":
		form = ConsentForm(request.POST)
		if form.is_valid():
			p.consent = True
			p.consent_age = form.cleaned_data.get('age')
			p.consent_questions = form.cleaned_data.get('questions')
			p.save()
			return redirect('instructions')
	context = {'form': form}
	context.update(nav(2,p=p))
	return render(request, "consent.html", context)

def instructions(request):
	records = check_init(request, 'pretest')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	return render(request, "local_instructions.html", nav(3,p=records['participant']))

def practice(request):
	records = check_init(request, 'pretest')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	treat = Experiment.fake_treatment(conditions=['global_control'], time=30, group='practice' )
	context = {}
	for i, p in enumerate(treat.participants):
		context['context'+str(i)] = p.diagram_context
		context['form'+str(i)] = p.form_context
	context.update(nav(4,p=records['participant']))
	return render(request, 'practice.html', context)

def pretest(request):
	records = check_init(request, 'pretest')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	part = records['participant']
	form = QuizForm()
	if request.method == 'POST':
		form = QuizForm(request.POST)
		if form.is_valid():
			part.passed_quiz = True
			part.save()
		else:
			part.pretest_tries += 1
			part.save()

	if part.passed_quiz:
		return redirect('start')
	else:
		context = { 'context': Experiment.quiz_treatment().condition.p1.diagram_context, 'form': form }
		context.update(nav(5,p=part))
		return render(request, "pretest.html", context)

def start(request):
	records = check_init(request,'start')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	if p.group == 'mturk':
		exp = Experiment.mturk()
	elif p.group == 'e327':
		exp = Experiment.e327()
	elif p.group == 'coop':
		exp = Experiment.coop()
	else:
		return not_configured_error(request,p)
	exp.queued.add(p)
	exp.save()
	context = nav(6,p=p)
	context['pk'] = p.pk
	context['turkSubmitTo'] = p.turkSubmitTo
	context['assignmentId'] = p.assignmentId
	return render(request, 'start.html', context)

def game(request):
	records = check_init(request,'game')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	context = nav(7,p=p)
	context['context']=p.game_context
	return render(request, 'game2.html', context)

def survey(request):
	records = check_init(request,'survey')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	form = None
	if not p.ended:
		now = datetime.utcnow().replace(tzinfo=utc)
		p.ended = now
		p.save()
	if request.method == 'POST':
		if str(request.POST.get('survey-surveyer', None)) == str(p.pk):
			sform = SurveyForm(p.pk, request.POST, prefix='survey', )
			#b5form = BIG5Form(request.POST, prefix='big5')
			machform = MACHIVForm(request.POST, prefix='machiv')
			#if sform.is_valid() and b5form.is_valid() and machform.is_valid():
			if sform.is_valid() and machform.is_valid():
				p.survey = sform.save()
				#p.big5 = b5form.save()
				p.machiv = machform.save()
				p.save()
				#p.big5.create_score()
				p.machiv.create_score()
				return redirect('end')
			else:
				#form = {'survey': sform, 'big5': b5form, 'machiv': machform}
				form = {'survey': sform, 'machiv': machform}
	context = nav(8,p=p)
	context['context']=p.survey_context
	if form:
		context['context'].update(form)
	return render(request, 'survey.html', context)

def end(request):
	records = check_init(request,'end')
	if 'redirect' in records and records['redirect'] != None:
		return records['redirect']
	p = records['participant']
	context = nav(8,p=p)
	context['p_str'] = str(p)
	return render(request, 'end.html', context)

#### ERROR PAGES #####
def error(request, msg, participant=None):
	return render(request, 'error.html', {'msg': msg, 'p_num': str(participant)})
def not_configured_error(request, p=None):
	return error(request, 'It appears the experiment was not configured correctly because your id was lost. Try accessing it again after closing your browser. Also, ensure that  '+ 
			'you have cookies enabled.', p)
def error500(request, *args, **kwargs):
	return error(request, "There was a server error.")
def error404(request, *args, **kwargs):
	return error(request, "Page not found.")

#### DEVELOPER ####
def dev_survey(request):
	treat = Experiment.fake_treatment()
	treat.advance_to_end()
	context = { 'context': treat.condition.p0.form_context }
	return render(request, 'survey.html', context)

def basic(request):
	parts = []
	for i in range(3):
		p = Participant()
		p.save()
		parts.append(p)
	request.session['part_num'] = parts[0].pk

	exp = Experiment(time_limit=30)
	exp.save()
	treat = exp.new_treatment(parts)
	turn = parts[0].turn
	context = {}
	for i, p in enumerate(parts):
		context['context'+str(i)] = p.diagram_context
		context['form'+str(i)] = p.form_context
	return render(request, 'main.html', context)

