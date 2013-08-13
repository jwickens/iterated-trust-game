from django.utils import simplejson
from django.shortcuts import redirect, render
from game.models import Participant, Experiment, Treatment
from form import ConsentForm, TransferForm, ReturnForm, QuizForm, TransitionForm
from django.http import HttpResponse

def checkin(request, p_id, game_state):
	p_num = request.session.get('part_num')
	if not p_num:
		refresh = True
	p = Participant.objects.get(id=p_id)
	p.treatment.update()
	refresh = False
	survey = False
	checkinURL = '/trustgame/json/checkin/'+p_id+'/'+p.game_state
	new_game_state = p.game_state
	if new_game_state != game_state:
		refresh = True
	if new_game_state == 'completed':
		survey = True
	return HttpResponse(simplejson.dumps({'refresh': refresh, 'survey': survey, 'checkinURL': checkinURL}), content_type="application/json")

def loadscreen(request, p_id):
	p = Participant.objects.get(id=p_id)
	state = p.game_state
	if state == "transition":
		return render(request, 'transition.js', {'context': p.diagram_context })
	elif state == 'ready' and p.condition.game_state == 'transition':
		return render(request, 'wait.js', {'context': p.diagram_context})
	else:
		return render(request, 'diagram.js', {'context': p.diagram_context})

def loadhistory(request, p_id):
	p = Participant.objects.get(id=p_id)
	treat = p.treatment
	data = ''
	turns = treat.condition.turns.filter(num__lte=treat.condition.turn_num).order_by('-num')
	for t in turns:
		data += '<tr>'
		data += "<td class='aligncenter'>"+str(t.num+1)+'</td>'
		if t.transferer_ready:
			data += '<td>'+t.transfer_actions(p)+'</td>'
		if t.completed:
			data += '<td>'+t.return_actions(p)+'</td>'
		data += '</tr>'
	return HttpResponse(simplejson.dumps({'actions': data,}), content_type='application/json')

def loadform(request, p_id=None, participant=None, context_update=None):
	if p_id:
		p = Participant.objects.get(id=p_id)
	else:
		p = participant
	state = p.game_state
	context = p.form_context
	if context_update:
		context.update(context_update)
	if state == "ready" or state == 'receive':
		return render(request, 'wait_form.html', {'context': context})
	elif state == "transition":
		return render(request, "transition_form.html", {'context': context })
	else:
		return render(request, 'game_form.html', {'context': context })

def submit(request, p_id):
	p = Participant.objects.get(id=p_id)
	state = p.game_state
	treatment = p.treatment
	game_id = p.game_id
	condition = treatment.condition
	others = treatment.others
	turn = treatment.turn
	tokens = turn.total_transfer_for(p.game_id)
	exp = treatment.experiment
	form = None

       	if state == "transition" and str(request.POST.get('p_num', None)) == str(p.pk):
       		transform = TransitionForm(p.pk, condition, request.POST)
       		if transform.is_valid():
       			condition.activate(p)
       			form = { 'as_p': 'Please wait while the other participants finish reading the instructions.' }
       		else:
       			form = {'form': transform}
       	elif state == "transfer" and str(request.POST.get('transferer', None)) == str(p.pk):
       		tform = TransferForm(p, exp, condition, others, request.POST)
       		if tform.is_valid():
       			arr = [ tform.cleaned_data.get('transfer0',0), tform.cleaned_data.get('transfer1',0), tform.cleaned_data.get('transfer2',0) ]
       			tokens = 0
       			turn.transfer( game_id, arr, tform.cleaned_data.get('tokens') )
       			for i in range(3):
       				if not i==game_id:
       					if tform.cleaned_data.get('default_'+str(i)) == True:
       						setattr(condition,'default_transfer'+str(game_id)+str(i), arr[i])
       			condition.save()
       		else:
       			form = {'form': tform}
       	elif state == "return" and str(request.POST.get('returnee', None)) == str(p.pk):
       		rform = ReturnForm(p, condition, tokens, request.POST)
       		if rform.is_valid():
       			tokens = 0
       			turn.make_return(p.game_id, rform.cleaned_data.get('return_amnt'), rform.cleaned_data.get('tokens'))
			setattr(condition, 'default_return'+str(game_id), str(float(rform.cleaned_data.get('default_return'))/100))
       			condition.save()
       		else:
       			form = {'form': rform}
       	else:
       		print "Incorrect Submit Request"


	treatment.update()
	return loadform(request, participant=p, context_update=form)

def queue(request, p_id, focus):
	p = Participant.objects.get(id=p_id)
	refresh = False
	if p.group == 'mturk':
		exp = Experiment.mturk()
	elif p.group == 'coop':
		exp = Experiment.coop()
	else:
		print "Incorrect Queue init"
		return redirect('portal')
	if p.treatment:
		refresh = True
	n = p.checkin(exp,focus)
	return HttpResponse(simplejson.dumps({'n': n, 'refresh': refresh}),  content_type="application/json")

def verify(request, p_id):
	p = Participant.objects.get(id=p_id)
	if p.passed_quiz:
		return HttpResponse(simplejson.dumps({'submit': True}),  content_type="application/json")
	else:
		return HttpResponse(simplejson.dumps({'submit': False}),  content_type="application/json")


