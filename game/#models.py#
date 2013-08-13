from django.db import models
from form import ConsentForm, TransferForm, ReturnForm, QuizForm, TransitionForm
from exitsurvey import SurveyForm, MACHIVForm, BIG5Form, ExitSurvey, MACHIV, BIG5
from random import shuffle
from datetime import datetime, timedelta
from django.utils.timezone import utc
import logging

logger = logging.getLogger(__name__)

class PlayerIndexed():
	## That is, fields are indexed by players.
	## Helper utilities
	# one player, many fields
	def set_state(self, game_id, field_dict):
		for field in field_dict:
			self._set( field, game_id, field_dict[field] )
	# many players, one field
	def set_field(self, kind, id_dict):
		for ident in id_dict:
			self._set(kind, ident, id_dict[ident])
	def _get(self, kind, game_id):
		return getattr(self,kind+str(game_id))

	def _set(self, kind, game_id, value):
		setattr(self, kind+str(game_id), value)
		self.save()

	def get_array(self, kind):
		arr = [ ]
		for i in range(3):
			arr.append(getattr(self,kind+str(i)))
		return arr

	def get_dict(self, kinds):
		d = { }
		for k in kinds:
			for i in range(3):
				d[k+str(i)] = getattr(self,k+str(i))
		return d
	def set_array(self, kind, arr):
		for i, x in enumerate(arr):
			self._set(kind,i,x)

class Participant(models.Model):
	## FIELDS
	# MTurk/Experimental Variables
	hitId		= models.CharField(max_length=100, null=True, default=None)
	assignmentId	= models.CharField(max_length=100, null=True, default=None)
	workerId	= models.CharField(max_length=100, null=True, default=None)
	turkSubmitTo	= models.CharField(max_length=100, null=True, default=None)
	base_pay	= models.DecimalField(null=True, max_digits=10, decimal_places=3)
	bonus_pay	= models.DecimalField(null=True, max_digits=10, decimal_places=3)
	consent		= models.BooleanField(default=False)
	consent_age	= models.IntegerField(null=True)
	consent_questions=models.CharField(max_length=200, null=True)
	passed_quiz 	= models.BooleanField(default=False)
	pretest_tries	= models.IntegerField(default=0)
	turn_num	= models.IntegerField(default=0)
	# Survey
	survey = models.ForeignKey('ExitSurvey', null=True)
	#big5 = models.ForeignKey('BIG5', null=True)
	machiv = models.ForeignKey('MACHIV', null=True)
	## LOGIC -- CLIENT
	# Logic Variables
	group		= models.CharField(max_length=100, null=True, default=None)
	treatment	= models.ForeignKey('Treatment', null=True, default=None)
	timestamp	= models.DateTimeField(null=True) # Queue.
	focus_timestamp	= models.DateTimeField(null=True) # Queue.
	started 	= models.DateTimeField(null=True) # .
	ended 		= models.DateTimeField(null=True) # .
	@property
	def machiv_score(self):
		if self.machiv:
			return self.machiv.score
		else:
			return None
	def get_survey(self, attr):
		if self.survey:
			return getattr(self.survey, attr)
		else:
			return None
	@property
	def total_time(self):
		if self.started and self.ended:
			diff = self.ended - self.started
			return diff.total_seconds()
		else:
			return None
	@classmethod
	def create(cls, **kargs):
		p = cls(**kargs)
		p.save()
		return p
	@classmethod
	def fake(cls, **kwargs):
		p = cls.objects.filter(group='participant_fake')
		if len(p) > 0:
			return p[0]
		else:
			return cls.create(group='participant_fake')


	@property
	def turn(self):
		return self.treatment.turn
		#return self.get_turn(tnum = self.turn_num, cnum = self.cond_num)
	def get_turn(self, tnum, cnum ):
		return self.treatment.get_condition(cnum).get_turn(tnum)
	@property
	def all_turns(self, cnum):
		return self.treatment.get_condition(cnum).turns.all()
	@property
	def  condition(self):
		return self.treatment.condition
	@property
	def experiment(self):
		return getattr(Experiment,self.group.split('-')[0])()
	@property
	def color(self):
		return self.condition._get('color',self.game_id)
	@property
	def shape(self):
		return self.condition._get('shape',self.game_id)
		#return self.get_shape(cnum=self.cond_num)
	def get_shape(self, cnum):
		return self.get_condition(cnum)._get('shape',self.game_id)
	@property
	def game_id(self):
		return self.condition.get_game_id(self)
		#return self.get_game_id(self.cond_num)
	def get_game_id(self, cnum):
		return self.treatment.get_condition(cnum).get_game_id(self)
	@property
	def game_state(self):
		return self.get_game_state()
	def get_game_state(self):
		return self.treatment.get_status(self)
	@property
	def tokens(self):
		state = self.game_state
		if state == "return":
			return self.turn.total_transfer_for(self.game_id)
		elif state == "transfer":
			return self.treatment.experiment.endowment
		else:
			return "None"
	def __str__(self):
		return str(self.group) + str(self.pk)
	@property
	def self_msg(self):
		return "You are the " + self.shape + "."
	@property
	def earnings(self):
		return sum([ c.get_earnings(self) for c in self.treatment.conditions.all() ])
	@property
	def others(self):
		return self.treatment.participants.exclude(pk=self.pk)
	@property
	def form(self):
		state = self.game_state
		context = {
			'treatment': self.treatment,
			'earnings': self.earnings,
			'exp': self.treatment.experiment,
			'tokens': self.tokens,
			'color': self.color,
			}
		if state == "transition":
			context.update({
				'form': TransitionForm(self.pk, self.condition),
				})
		if state == "completed":
			context.update(self.survey_context)
		if state == "transfer":
			context.update({
				'form' : TransferForm(self, self.treatment.experiment, self.condition, self.others),
			})
		if state == "return":
			context.update({
				'form': ReturnForm(self, self.condition, self.turn.total_transfer_for(self.game_id)),
				})
		return context
	@property
	def context(self):
		return  {
			'shape': self.shape,
			'pk': self.pk,
			'self_msg': self.self_msg,
			'tokens': self.tokens,
			'earnings': self.earnings,
			'game_state': self.game_state,
			'game_id': self.game_id,
			'group': self.group
			}
	@property
	def game_context(self):
		pcontext = self.context
		pcontext.update(self.form)
		pcontext.update(self.turn.context)
		return pcontext
	@property
	def survey_context(self):
		return {
				'survey': SurveyForm(self.id, prefix='survey'),
				'machiv': MACHIVForm(prefix='machiv'),
				#'big5': BIG5Form(prefix='big5'),
			}
	
	@property
	def form_context(self):
		fcontext = self.form
		fcontext.update(self.context)
		return fcontext

	@property
	def diagram_context(self):
		pcontext = self.context
		pcontext.update(self.turn.context)
		return pcontext
	def checkin(self, experiment, focus):
		now = datetime.utcnow().replace(tzinfo=utc)
		self.timestamp = now
		if focus=='true':
			self.focus_timestamp = now
		self.save()
		return experiment.update()

class Turn(PlayerIndexed, models.Model):
	## PARENTS
	@property
	def condition(self):
		return Condition.objects.get(turns__pk=self.pk)
	@property
	def treatment(self):
		return self.condition.treatment
	@property
	def experiment(self):
		return self.treatment.experiment

	## FIELDS
	num = models.IntegerField()

	# the game_id's of the roles
	transferer = models.IntegerField()
	returnee1 = models.IntegerField()
	returnee2 = models.IntegerField()
	def get_participant(self, game_id):
		return self.condition._get('p', game_id)
	def get_role(self, game_id):
		if self._get('timestamp',game_id):
			return "ready"
		else:
			roles = {'transfer0': self.transferer, 'return1': self.returnee1, 'return2': self.returnee2}
			for role in roles:
				if game_id == roles[role]:
					if not self.transferer_ready and role != "transfer0":
						return "receive"
					else:
						return role[:-1]
	@property
	def others(self):
		return [ self.condition._get('p', self.returnee1), self.condition._get('p', self.returnee2) ]

	# these are indexed by participant game_id
	transfer0 = models.IntegerField(default=0)
	transfer1 = models.IntegerField(default=0)
	transfer2 = models.IntegerField(default=0)
	@property
	def transfers(self):
		return self.get_array("transfer")
	@transfers.setter
	def transfers(self, arr):
		self.set_array('transfer', arr)
	def total_transfer_for(self, game_id):
		return self._get('transfer', game_id) * self.experiment.transfer_multiplier

	return0 = models.IntegerField(default=0)
	return1 = models.IntegerField(default=0)
	return2 = models.IntegerField(default=0)
	@property
	def returns(self):
		return self.get_array("return")
	@returns.setter
	def returns(self, arr):
		self.set_array('return', arr)	

	earnings0 = models.IntegerField(default=0)
	earnings1 = models.IntegerField(default=0)
	earnings2 = models.IntegerField(default=0)
	@property
	def earnings(self):
		return self.get_array("earnings")
	@returns.setter
	def returns(self, arr):
		self.set_array('earnings', arr)	
		
	label0 = models.CharField(max_length=50, default='entering\nexperiment')
	label1 = models.CharField(max_length=50, default='entering\nexperiment')
	label2 = models.CharField(max_length=50, default='entering\nexperiment')
	@property
	def labels(self):
		return self.get_array('label')
	@labels.setter
	def labels(self, arr):
		self.set_array('label', arr)

	activated = models.DateTimeField(null=True)
	timestamp0 = models.DateTimeField(null=True) #If transferer, when state created; if returner, when game_state changed from receive to reutrn.
	timestamp1 = models.DateTimeField(null=True)
	timestamp2 = models.DateTimeField(null=True)
	default0   = models.BooleanField(null=False) #If the decision was made by default
	default1   = models.BooleanField(null=False) #If the decision was made by default
	default2   = models.BooleanField(null=False) #If the decision was made by default
	@property
	def timestamps(self):
		return self.get_array('timestamp')
	@property
	def now(self):
		return datetime.utcnow().replace(tzinfo=utc)
	def get_lagged_var(self, var):
		t = self.lagged_turn
		if t:
			return getattr(t,var)
		else:
			return None
	@property
	def avg_return(self):
		return sum(self.get_array('return'))/2
	@property
	def lagged_turn(self):
		try:
			return self.condition.turns.get(num=(self.num-1))
		except:
			return None

	def get_shape_or_self(self, p):
		def func(p_num):
			if p_num == p.game_id:
				return 'you'
			else:
				return self.get_participant(p_num).shape.capitalize()
		return func
	def wrap_p(self, arr):
		string = ''
		for action in arr:
			string += '<p>'+action+'</p>'
		return string
	def transfer_actions(self, p):
		arr = []
		transferer = self.transferer
		shapegetter = self.get_shape_or_self(p)
		if self.condition.info_condition == 'local' and transferer != p.game_id:
			transferer_actions = [p.game_id]
		else:
			transferer_actions = range(3)
			transferer_actions.remove(transferer)
		for i in transferer_actions:
			amnt = self._get('transfer', i)
			arr.append(shapegetter(transferer).capitalize() + " transfered " + str(amnt) + ' x 3 = ' + str(amnt*3) + ' to ' + shapegetter(i))
		return self.wrap_p(arr)
	def return_actions(self, p):
		arr = []
		transferer = self.transferer
		shapegetter = self.get_shape_or_self(p)
		if self.condition.info_condition == 'local' and transferer != p.game_id:
			returners = [p.game_id]
		else:
			returners = [ self.returnee1, self.returnee2 ]
		for r in returners:
			amnt = self._get('return', r)
			arr.append(shapegetter(r).capitalize() + ' returned ' + str(amnt) + ' back to ' + shapegetter(transferer))
		return self.wrap_p(arr)

	## LOGIC
	def activate(self):
		self.activated = self.now
		self.save()
		return_label = "Waiting\\non\\n"+self.condition._get('p',self.transferer).shape.capitalize()
		self.set_field('label', {
				self.transferer: "Transfer",
				self.returnee1: return_label,
				self.returnee2:  return_label,
				})

	def transfer(self, game_id, arr, p_earnings):
		self.set_state(game_id, {
				'earnings': p_earnings,
				'timestamp': self.now,
				})
		self.set_field('label', {
				self.transferer: "Waiting\\non\\nothers",
				self.returnee1: "Return",
				self.returnee2: "Return",
				})
		self.transfers = arr
	@property
	def transferer_ready(self):
		return self._get('timestamp', self.transferer) != None

	def make_return(self, game_id, returns, tokens):
		self.set_state(game_id, {
				'return': returns,
				'earnings': self._get('earnings',game_id) + tokens,
				'timestamp': self.now,
				'label': "Ready!"
				})
	@property
	def completed(self):
		return self.timestamp0 != None and self.timestamp1 != None and self.timestamp2 != None
	def complete(self):
		self.timestamp0 = self.now
		self.timestamp1 = self.now
		self.timestamp2 = self.now
		self.save()

	def get_expired_participants(self):
		time_limit = self.experiment.time_limit
		now = self.now
		if not time_limit or not self.activated:
			return []
		limit = timedelta(seconds=time_limit)
		if not self.transferer_ready:
			if now - self.activated > limit:
				return [self.transferer]
			else:
				return []
		else:
			guilty = range(3)
			guilty.remove(self.transferer)
			if now - self._get('timestamp', self.transferer) < limit:
				return []
			else:
				for i in guilty:
					if self._get('timestamp', i):
						guilty.remove(i)
				return  guilty

	def update(self):
		expired = self.get_expired_participants()
		for i in expired:
			self._set('default', i, True)
			if self.transferer_ready:
				tokens =  self.total_transfer_for(i)
				amnt = int(self.condition._get('default_return',i) * tokens)
				self.make_return(i, amnt, tokens - amnt)
			else:
				self.transfer(i, *self.condition.default_transfers_for(i))

	## CLIENT
	@property
	def context(self):
		condition = self.condition
		treatment = condition.treatment
		num = self.num
		T = condition.transfer_matrix()
		R = condition.return_matrix()
		last_transferer = None
		first_transferer = None
		last_returners = None
		first_returners = None
		if self.transferer_ready:
			last_transferer = self.transferer
			if num > 2:
				first_turn = condition.get_turn(num-3)
				first_returners = [ first_turn.returnee1, first_turn.returnee2 ]
		else:
			if num > 0:
				prev_turn = condition.get_turn(num-1)
				#last_returners = [ prev_turn.returnee1, prev_turn.returnee2 ]
				last_returners = [ prev_turn.transferer ]
			if num > 2:
				first_turn = condition.get_turn(num-3)
				first_transferer = [ first_turn.transferer ]
		if condition.game_state == "transition":
			#time_passed = self.now - condition.activated
			#time_limit = condition.experiment.time_limit_quiz - time_passed.total_seconds()
			time_limit = condition.experiment.time_limit_quiz
		else:
			#time_passed = self.now - self.activated
			#time_limit = condition.experiment.time_limit - time_passed.total_seconds()
			time_limit = condition.experiment.time_limit

		context = {
			'time_limit': time_limit,
			'exp': self.treatment.experiment,
			'turn_num': num,
			'treatment': treatment,
			'condition': condition,
			'last_transferer': last_transferer,
			'first_transferer': first_transferer,
			'last_returners': last_returners,
			'first_returners': first_returners,
			's01': T[0][1],
			's10': T[1][0],
			's20': T[2][0],
			's02': T[0][2],
			's21': T[2][1],
			's12': T[1][2],
			'r01': R[0][1],
			'r10': R[1][0],
			'r20': R[2][0],
			'r02': R[0][2],
			'r21': R[2][1],
			'r12': R[1][2],
			'label0': self.label0,
			'label1': self.label1,
			'label2': self.label2
		}
		context.update(condition.context)
		return context
class Condition(PlayerIndexed, models.Model):
	## PARENTS
	@property
	def treatment(self):
		return Treatment.objects.get(conditions__pk = self.pk)
	@property
	def experiment(self):
		return self.treatment.experiment
	## FIELDS
	num = models.IntegerField()
	# conditions
	link_condition = models.CharField(max_length=50, default="unrestricted")
	info_condition = models.CharField(max_length=50, default="global")
	@property
	def condition(self):
		return self.link_condition + "_" + self.info_condition	
	
	
	activated = models.DateTimeField(null=True)
	timestamp0 = models.DateTimeField(null=True) #when players pass the condition quiz
	timestamp1 = models.DateTimeField(null=True)
	timestamp2 = models.DateTimeField(null=True)
	expired0 = models.BooleanField(default=False) # When players don't pass the condition quiz on time
	expired1 = models.BooleanField(default=False)
	expired2 = models.BooleanField(default=False)
	@property
	def now(self):
		return datetime.utcnow().replace(tzinfo=utc)
	@property
	def game_state(self):
		if bool(self.timestamp0 and self.timestamp1 and self.timestamp2):
			return "initialized"
		else:
			return "transition"
	# participants
	p0 = models.ForeignKey('Participant',related_name='+')
	p1 = models.ForeignKey('Participant',related_name='+')
	p2 = models.ForeignKey('Participant',related_name='+')
	@property
	def participants(self):
		return self.get_array('p')
	@participants.setter
	def participants(self, arr):
		self.set_array('p', arr)
	@property
	def others(self):
		return self.turn.others
	def get_game_id(self, participant):
		return self.participants.index(participant)
	def get_transferer(self, tnum):
		return self.get_turn(tnum).transferer
	def get_others(self, tnum):
		parts = self.participants
		del parts[self.get_transferer(tnum)]
		return parts
	def get_role(self, p):
		if self.game_state == "transition":
			if self._get('timestamp', self.get_game_id(p)):
				return "ready"
			else:
				return "transition"
		else:
			return self.turn.get_role(self.get_game_id(p))
	def get_all_turns_as_transferer(self,p):
		return self.turns.filter(transferer=p.game_id)
	def get_all_returns(self,p):
		returns = 0
		turns = self.get_all_turns_as_transferer(p)
		for t in turns:
			returns += sum(t.returns)
		return returns
	def get_earnings(self, participant):
		earnings = 0
		for t in self.turns.all():
			earnings += t._get('earnings', self.get_game_id(participant))
		return earnings + self.get_all_returns(participant)
	# participant shapes
	shape0 = models.CharField(max_length = 50, default = "circle")
	shape1 = models.CharField(max_length = 50, default = "square")
	shape2 = models.CharField(max_length = 50, default = "triangle")
	@property
	def shapes(self):
		return self.get_array('shape')
	@shapes.setter
	def shapes(self, arr):
		self.set_array('shape', arr)
	# participant colors
	color0 = models.CharField(max_length = 50, default = "red")
	color1 = models.CharField(max_length = 50, default = "#00CBE7")
	color2 = models.CharField(max_length = 50, default = "#00DA3C")
	@property
	def colors(self):
		return self.get_array('color')
	@colors.setter
	def colors(self, arr):
		self.set_array('color', arr)
	# turns
	turns = models.ManyToManyField(Turn)
	turn_num = models.IntegerField(default=0) # keeps track of current turn
	valid_turns = models.IntegerField(default=0)
	@property
	def turn(self):
		return self.get_turn(self.turn_num)
	def get_turn(self, num):
		return self.turns.get(num=num)
	# Defaults
	default_return0 = models.FloatField(default=0.0)
	default_return1 = models.FloatField(default=0.0)
	default_return2 = models.FloatField(default=0.0)
	default_transfer01 = models.IntegerField(default=0)
	default_transfer02 = models.IntegerField(default=0)
	default_transfer12 = models.IntegerField(default=0)
	default_transfer10 = models.IntegerField(default=0)
	default_transfer20 = models.IntegerField(default=0)
	default_transfer21 = models.IntegerField(default=0)
	def default_transfers_for(self, game_id):
		transfers = []
		total = 0
		for i in range(3):
			if game_id == i:
				transfers.append(0)
			else:
				amnt = getattr(self, 'default_transfer'+str(game_id)+str(i))
				total += amnt
				transfers.append(amnt)
		return [ transfers, self.experiment.endowment - total ] 

	## INIT
	@classmethod
	def create(cls, participants, rounds, link_condition, info_condition, num):
		turns = rounds * 3
		obj = cls( link_condition = link_condition, info_condition = info_condition, p0 = participants[0], p2 = participants[2], p1 = participants[1], num=num)
		obj.save()
		for i in range(turns):
			tarr = [ ( ( (i % 3) + k ) % 3 ) for k in range(3) ] # maps participants to roles
			t = Turn(
				transferer = tarr[0],
				returnee1  = tarr[1],
				returnee2  = tarr[2],
				num = i,
				)
			t.save()
			obj.turns.add(t)
			obj.save()
		return obj
	## LOGIC
	@property
	def completed(self):
		return (len(self.turns.all()) - 1) == self.turn_num and self.turn.completed
	def validate_turns(self):
		i=0
		for t in self.turns.all():
			if t.completed:
				i+=1
		self.valid_turns = i
		self.save()
		
	def get_expired_participants(self):
		assert self.game_state == "transition"
		time_limit = self.experiment.time_limit_quiz
		if not time_limit:
			return []
		limit = timedelta(seconds=time_limit)
		if self.now - self.activated > limit:
			guilty = range(3)
			for i in guilty:
				if self._get('timestamp', i):
					guilty.remove(i)
			return  guilty
		else:
			return []

	def init(self):
		self.activated = self.now
		self.save()
	def activate(self, p):
		self._set('timestamp', self.get_game_id(p), self.now)
		if self.game_state == "initialized":
			self.turn.activate()
	def step(self):
		assert not self.completed
		if self.game_state == "transition":
			expired = self.get_expired_participants()
			if expired:
				for i in expired:
					self._set('expired',i,True)
					self._set('timestamp', i, self.now)
				self.turn.activate()
		else:
			self.turn.update()
			if self.turn.completed:
				self.turn_num += 1
				self.turn.activate()
				self.save()

	def advance_to_end(self):
		self.turn.complete()
		while not self.completed:
			self.turn_num+= 1
			self.turn.complete()
			self.save()

	## CLIENT
	def transfer_matrix(self, num=None):
		if num == None:
			num = self.turn_num
		if self.turn.transferer_ready:
			num += 1
		return self._matrix('transfers', num)
	def return_matrix(self, num=None):
		if num==None:
			num = self.turn_num
		#if self.get_turn(num).timestamp0: #We can't show the current transfer if the transferer hasn't decided yet, instead we should show the old transfers
		#	num += 1
		return self._matrix('returns', num)
	@property
	def instructions(self):
		link_condition_msg = {
				'control': 'you may only transfer up to 10 tokens to either of the other players.',
				'pick1': 'you may only transfer tokens to one of the other players.',
				'unrestricted': 'you may transfer as many of your tokens as you would like to the other players.'
				}
		info_condition_msg = {
				'global': 'you may see all transfers and returns in the experiment, including those between other players.',
				'local': 'you may only see those transfers that are between yourself and the other players.'
				}
		if self.num < 1:
			msg = "To start out you will play a few rounds where " + link_condition_msg[self.link_condition] + " In addition, " + info_condition_msg[self.info_condition]
		else:
			msg = ( "You will now start a new game, with new identities. Other players cannot know if you are the same shape or not. In this game "
					+ link_condition_msg[self.link_condition] + " In addition, " + info_condition_msg[self.info_condition] )
		return msg
	@property
	def context(self):
		context = { 'instructions': self.instructions,}
		context.update(self.get_dict(['shape', 'color', 'p']))
		return context
	## Helper utilities
	def _matrix(self, kind, i):
		#Creates a matrix of the transfers from the last 3 turns, aka the current round
		#if (not self.get_turn(i).transferer_ready): #We can't show the current transfer if the transferer hasn't decided yet, instead we should show the old transfers
		i -= 1
		if i < 2:
			i = 2
		matrix = [ getattr(turn, kind) for turn in self.turns.filter(num__lt=i+1).filter(num__gt=i-3).order_by('transferer') ]
		return matrix


class Treatment(models.Model):
	## PARENTS
	@property
	def experiment(self):
		return Experiment.objects.get(treatments__pk = self.pk)
	## FIELDS
	# Controls
	valid = models.BooleanField(default=False) #completed
	valid_participants = models.BooleanField(default=False)
	def get_status(self, participant):
		if self.completed:
			return 'completed'
		else:
			return self.condition.get_role(participant)
	# Participants
	@property
	def participants(self):
		return Participant.objects.filter(treatment__pk = self.pk).order_by('pk')
	@property
	def others(self):
		return self.condition.others
	# Conditions
	label = models.CharField(max_length=50)
	conditions = models.ManyToManyField(Condition)
	condition_num = models.IntegerField(default=0)
	valid_conditions = models.IntegerField(null=True)
	@property
	def condition(self):
		return self.get_condition(self.condition_num)
	def get_condition(self, num):
		return self.conditions.get(num=num)
	@property
	def turn(self):
		return self.condition.turn
	def __str__(self):
		return "<treatment"+str(self.pk)+": "+self.label + ">"
	## INIT
	@classmethod
	def create(cls, participants, label, condition_list, rounds_per_condition):
		t = cls( label = label )
		t.save()
		for i, c in enumerate(condition_list):
			cond = c.split('_')
			info_cond = cond[0]
			link_cond = cond[1]
			shuffle(participants)
			condition = Condition.create(participants, rounds_per_condition, link_cond, info_cond, i)
			t.conditions.add(condition)
		t.save()
		t.condition.init()
		return t
	## LOGIC
	@property
	def completed(self):
		return (len(self.conditions.all()) -1) == self.condition_num and self.condition.completed
	def validate_conditions(self):
		i = 0
		for c in self.conditions.all():
			c.validate_turns()
			if c.completed:
				i += 1
		self.valid_conditions = i
		self.save()

	def initialize(self):
		parts = self.participants
		for p in parts:
			self.condition.activate(p)

	def update(self):
		c = self.condition
		if c.completed:
			if not self.completed:
				self.condition_num += 1
				self.save()
				self.condition.init()
			else:
				if not self.valid_participants:
					self.validate_participants()
				if self.valid == False:
					self.validate_conditions()
					self.valid = True
					self.save()
		else:
			c.step()

	def reset(self):
		self.new_turn(self.next_condition())
		self.reset_participants()
		for p in self.participants():
			p.step()
	def advance_to_end(self):
		self.condition.advance_to_end()
		while not self.completed:
			self.condition_num += 1
			self.save()
			self.condition.advance_to_end()
	
	def validate_participants(self):
		valid = True
		for p in self.participants:
			if not bool(p.passed_quiz):
				valid = False
			if p.group == 'mturk' and not bool(p.consent):
				valid = False
		self.save()

	def transfer_tokens_for(self, participant):
		return self.last_turn().get_by_id("transfer",participant.game_id) * self.transfer_multiplier



class Experiment(models.Model):
	## FIELDS
	# Experimental Parameters
	endowment = models.IntegerField(default=20)
	transfer_multiplier = models.IntegerField(default=3)
	earnings_multiplier = models.DecimalField(max_digits=10, decimal_places=10, default=0.002)
	max_on_control = models.IntegerField(default=10)
	rounds_per_condition = models.IntegerField(default=10)
	treatments = models.ManyToManyField('Treatment')
	time_limit = models.IntegerField(default=30) #60 seconds
	time_limit_quiz = models.IntegerField(default=300) #5 minutes to pass the quiz
	group = models.CharField(max_length=50, default='mturk') 
	
	# Logic
	queued = models.ManyToManyField('Participant')
	@property
	def queued_participants(self):
		limit = datetime.utcnow().replace(tzinfo=utc) - timedelta(seconds=20)
		return self.queued.exclude(timestamp__lt = limit)
	@property
	def queued_valid(self):
		limit = datetime.utcnow().replace(tzinfo=utc) - timedelta(seconds=10)
		return self.queued.exclude(focus_timestamp__lt = limit)

	treatment_schedule = {
		#	'A':	[ 'local_control', 'global_pick1'],
		#	'B':	[  'local_control', 'global_control'],
			'C':	[  'local_control', 'global_unrestricted'],
	#		'D':	[  'local_control', 'local_pick1'],
			'E':	[  'local_control', 'local_control'],
#			'F':	[  'local_control', 'local_unrestricted'],	
			}
	@property
	def treatment_counts(self):
		return self.count_treatments(valid=True)
	def count_treatments(self, **kwargs):
		counts = { }
		for key in self.treatment_schedule:
			counts[key] = 0
		for c in self.treatments.filter(**kwargs):
			counts[c.label] += 1
		return counts

	def new_treatment(self, participants, conditions=None, treatment_label=None):
		if not conditions:
			print 'creating a new treatment'
			counts = self.treatment_counts
			print(counts)
			least_used = min(counts, key=counts.get)
			print(least_used)
			treatments = [ key for key in counts if counts[key] == counts[least_used] ]
			print(treatments)
			shuffle(treatments)
			print(treatments)
			treatment_label = treatments[0]
			print(treatment_label)
			conditions = self.treatment_schedule[treatment_label]

		t = Treatment.create( participants, label = treatment_label,  condition_list = conditions, rounds_per_condition = self.rounds_per_condition )
		self.treatments.add(t)
		self.save()
		for p in participants:
			p.treatment = t
			p.save()

		return t
	@classmethod
	def mturk(cls):
		exp = cls.objects.filter(group='mturk')
		if len(exp)==0:
			exp = cls(group='mturk')
			exp.save()
		else:
			exp = exp[0]
		return exp
	@classmethod
	def e327(cls):
		exp = cls.objects.filter(group='e327', rounds_per_condition=5, time_limit=30)
		if len(exp)==0:
			exp = cls(group='e327')
			exp.save()
		else:
			exp = exp[0]
		return exp
	@classmethod
	def coop(cls):
		exp = cls.objects.filter(group='coop')
		if len(exp)==0:
			exp = cls(group='coop', rounds_per_condition=5, time_limit=30 )
			exp.save()
		else:
			exp = exp[0]
		return exp
	@classmethod
	def fake_treatment(cls, time=0, initialize=True, conditions=None, group='fake'):
		parts = []
		for i in range(3):
			px = Participant(group=group)
			px.save()
			parts.append(px)
		exp = cls(time_limit=time, group=group, rounds_per_condition=99 )
		exp.save()
		treat = exp.new_treatment(parts, conditions=conditions, treatment_label=group)
		if initialize:
			treat.initialize()
		return treat
	@classmethod
	def quiz_treatment(cls):
		exp = cls.objects.filter(group='fake_quiz')
		if len(exp) == 0:
			treat = cls.fake_treatment(group='fake_quiz', conditions=['local_control',])
			def go_circle():
				treat.turn.transfer(0, [0,7,7],0)
				treat.turn.make_return(1, 9, 0)
				treat.turn.make_return(2, 7, 0)
				treat.update()
			def go_square():
				treat.turn.transfer(1, [6,0,11],0)
				treat.turn.make_return(0, 6, 0)
				treat.turn.make_return(2, 15, 0)
				treat.update()
			def go_triangle():
				treat.turn.transfer(2, [1,6,0],0)
				treat.turn.make_return(0, 15, 0)
				treat.turn.make_return(1, 7, 0)
				treat.update()
			for i in range(2):
				go_circle()
				go_square()
				go_triangle()
			go_circle()
			treat.turn.transfer(1, [6,0,15],0)
			treat.update()
			return treat
		else:
			return exp[0].treatments.get(label='fake_quiz')
	@classmethod
	def curb_treatment(cls):
		exp = cls.objects.filter(group='fake_curb')
		if len(exp) == 0:
			treat = cls.fake_treatment(group='fake_curb' , conditions=['local_control',])
			treat.turn.transfer(0, [0,4,9],0)
			treat.turn.make_return(1,2,0)
			treat.turn.make_return(2,18,0)
			treat.update()
			return treat
		else:
			return exp[0].treatments.get(label='fake_curb')
	def update(self):
		parts = self.queued_valid
		if len(parts) > 2:
			ps = parts[0:3]
			self.queued.remove(*ps)
			self.save()
			t = self.new_treatment(ps)
			for p in ps:
				p.treatment = t
				p.save()
		return len(self.queued_participants)
