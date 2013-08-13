from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class ConsentForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ConsentForm,self).__init__(*args, **kwargs)
		self.fields['consent'] = forms.BooleanField(label="In consideration of all of the above, I give my consent to participate in this research study." )
		self.fields['age'] = forms.IntegerField(min_value = 0, max_value=116, label="I am old enought to participate in this study. Please enter your age:")
		self.fields['questions'] = forms.CharField(required=False, label="Do you have any questions for us?")

	def clean(self):
		cleaned_data = super(ConsentForm, self).clean()

		if cleaned_data.get('consent') != True:
			self._errors['consent'] = self.error_class(['This experiment may not continue unless you give your consent.'])

		age = cleaned_data.get('age')
		if age < 18:
			self.errors['age'] = self.error_class(['You must be 18 or older to participate.'])

		return cleaned_data

class TransitionForm(forms.Form):
	def __init__(self, p_num, condition, *args, **kwargs):
		super(TransitionForm,self).__init__(*args,**kwargs)
		self.info_cond = condition.info_condition
		self.link_cond = condition.link_condition
		self.button = ( '<input type="submit" class="submitbutton" id="gamebutton'+str(condition.treatment.id)+str(p_num)+str(condition.turn_num)+
				'" name="quiz" value="Submit" />' )
		self.fields['p_num'] = forms.IntegerField(widget=forms.HiddenInput(), initial=p_num)
		self.fields['info'] = forms.ChoiceField([('y', 'yes'),('n','no')],
					label='1. If you are A, and the other players are B and C, can you see what B and C send to each other?')
		self.fields['link'] = forms.ChoiceField([('a', '0'),('b','10'),('c','15'),('d','20')],
					label=('2. Assume once again that you are A and that the others are B and C. You have already decided to send 5 tokens to B. What is the most'+
						' you could send to C?'))
		
	def clean(self):
		cleaned_data = super(TransitionForm, self).clean()
		if cleaned_data.get('info') == u'y' and self.info_cond == 'local':
			self._errors['info'] = self.error_class([u'In this condition you cannot see transfers or returns between other players.'])
			del cleaned_data['info']
		if cleaned_data.get('info') == u'n' and self.info_cond == 'global':
			self._errors['info'] = self.error_class([u'In this condition you can see transfers or returns between other players.'])
			del cleaned_data['info']
		if self.link_cond == 'control' and cleaned_data.get('link') != u'b':
			self._errors['link'] = self.error_class([u'In this condition you can send up to 10 tokens to either of the other players.'])
			del cleaned_data['link']
		if self.link_cond == 'pick1' and cleaned_data.get('link') != u'a':
			self._errors['link'] = self.error_class([u'Since you have already decided to send 5 tokens to B, you cannot send any to the other player.'])
			del cleaned_data['link']
		if self.link_cond == 'unrestricted' and cleaned_data.get('link') != u'c':
			self._errors['link'] = self.error_class([u'You can allocate all of your 20 tokens between the two players, therefore 20 - 5 tokens to B = 15.'])
			del cleaned_data['link']
		return cleaned_data

class QuizForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(QuizForm,self).__init__(*args, **kwargs)
		self.fields['who'] = forms.ChoiceField([('1','----'),('c', 'circle'),('q', 'square'), ('t', 'triangle')],
			label="1. In this turn, who is the transferrer?")
		self.fields['self'] = forms.ChoiceField([('1','----'),('c', 'circle'),('q', 'square'), ('t', 'triangle')],
			label="2. Who are you playing as?")
		self.fields['op'] = forms.ChoiceField([('1','----'), ('trans', 'transfer'), ('ret', 'return') ],
			label="3. What part of the turn is currently being played?")
		self.fields['circle_earnings'] = forms.ChoiceField([('1','----'),('y', 'yes'),('n','no')],
			label="4. In the previous turn, did the circle get more tokens back from square's return than the circle itself transfered to the square?")
		self.fields['prev_round'] = forms.ChoiceField([('1','----'),('y', 'yes'),('n','no')],
			label="5. In the diagram, can we see the square's transfers from the last round? (3 turns ago)")

	def clean(self):
		cleaned_data = super(QuizForm, self).clean()
		required = self.error_class([u'This field is required.'])
		who = cleaned_data.get('who')
		if who != u'q':
			if who == '1':
				self._errors['who'] = required
			else:
				self._errors['who'] = self.error_class([u'The transferrer will always have the label "transfer" or "waiting on others."'])
			del cleaned_data['who']
		sel = cleaned_data.get('self')
		if sel and sel != u'q':
			if sel == '1':
				self._errors['self'] = required
			else:
				self._errors['self'] = self.error_class([u'Your shape is written at the top of the diagram and can also be inferred from the History.'])
			del cleaned_data['self']
		op = cleaned_data.get('op')
		if op and op != u'ret':
			if sel == '1':
				self._errors['op'] = required
			else:
				self._errors['op'] = self.error_class([u'The labels, "waiting on others", "return", and "return" labels indicate that the transferrer has already made his' 
					+u' decision and that the other participants are making their return decision.'])
			del cleaned_data['op']
		cir = cleaned_data.get('circle_earnings')
		if cir and cir != 'y':
			if sel == '1':
				self._errors['circle_earnings'] = required
			else:
				self._errors['circle_earnings'] = self.error_class(
						[u'Make sure to compare the amount transfered before multiplication by 3. Also, transfers and their returns have the same color.'])
			del cleaned_data['circle_earnings']
		prev = cleaned_data.get('prev_round')
		if prev and prev != u'n':
			if sel == '1':
				self._errors['prev_round'] = required
			else:
				self.errors['prev_round'] = self.error_class([u'The square has just finished transferring, so we can only see his transfers from this round.'])
			del cleaned_data['prev_round']
			
		return cleaned_data

class TransferForm(forms.Form):
	def __init__(self, p, experiment, condition, others, *args, **kwargs):
		super(TransferForm,self).__init__(*args, **kwargs)
		p_num = p.pk
		self.exp = experiment
		self.condition = condition
		labels = []
		self.button = ( '<input type="submit" class="submitbutton" id="gamebutton'+str(condition.treatment.id)+str(p_num)+str(condition.turn_num)+
				'" name="transfer" value="Submit" />' )

		self.fields['tokens'] = forms.IntegerField(label="Keep:", validators=[MinValueValidator(0)])
		self.fields['transferer'] = forms.IntegerField(widget=forms.HiddenInput(), initial=p_num)
		for o in others:
			labels.append(("To the " + o.shape + ":",o.game_id))
			self.fields['default_'+str(o.game_id)] = forms.BooleanField(required=False, label="Transfer this amount on timeout. The current default is, "
					+str(getattr(condition, 'default_transfer'+str(p.game_id)+str(o.game_id) ) )
					)

		for l, i in labels:
			self.fields['transfer'+str(i)] = forms.IntegerField(label=l, validators=[MinValueValidator(0)])


	def clean(self):
		cleaned_data = super(TransferForm, self).clean()
		tokens = cleaned_data.get('tokens')
		trans = []
		for i in range(3):
			x = cleaned_data.get('transfer'+str(i))
			if x != None:
				if self.condition.link_condition == "control" and x > self.exp.max_on_control:
					raise forms.ValidationError("You can only transfer up to "+ str(self.exp.max_on_control) + " tokens per player.")
				else:
					trans.append(x)
				
		
		if len(trans)>=2 and (tokens or tokens == 0):
	
			if trans[0] + trans[1] + tokens > self.exp.endowment:
				raise forms.ValidationError(
				"Your total returns plus the tokens you keep must add up to " + str(self.exp.endowment) + " tokens. Please reduce one or both of your transfers and/or" 
				+ " how many tokens you will keep.")
	
			if trans[0] + trans[1] + tokens < self.exp.endowment:
				raise forms.ValidationError("Please allocate all of your tokens. Increase either how much you transfer or how much you will keep.")
			
			if self.condition.link_condition == "pick1":
				if trans[0] > 0 and trans[1] > 0:
					raise forms.ValidationError(
					"You may only transfer tokens to one of the other participants. Please indicate to whom you will not send tokens by entering 0 for that "+ 
					"participant."
					)
		else:
			raise forms.ValidationError("You must allocate all your tokens.")

		return cleaned_data


class ReturnForm(forms.Form):
	def __init__(self, p, condition, tokens, *args, **kwargs):
		super(ReturnForm, self).__init__(*args, **kwargs)
		p_num = p.pk
		self.button = ( '<input type="submit" class="submitbutton" id="gamebutton'+str(condition.treatment.id)+str(p_num)+str(condition.turn_num)+
				'" name="return" value="Submit" />' )
		self.tokens = tokens
		self.fields['tokens'] = forms.IntegerField(label="Keep:", validators=[MinValueValidator(0)])
		self.fields['return_amnt'] = forms.IntegerField(label="Return:", validators=[MinValueValidator(0)])
		self.fields['default_return'] = forms.IntegerField(
			validators=[MinValueValidator(0),MaxValueValidator(100)],
			label='% transfer to return on timeout',
			initial=str(int(getattr(condition, 'default_return'+str(p.game_id))*100))
			)
		self.fields['returnee'] = forms.IntegerField(widget=forms.HiddenInput(), initial=p_num)

	def clean(self):
		cleaned_data = super(ReturnForm, self).clean()
		r = cleaned_data.get("return_amnt")
		t = cleaned_data.get("tokens")
		if (r or r == 0) and (t or t ==0):
			msg = "Your return plus the amount you keep should equal " + str(self.tokens) + "."
			if r + t < self.tokens:
				raise forms.ValidationError("Please allocate all your tokens. " + msg )
			if r + t > self.tokens:
				raise forms.ValidationError("You cannot allocate more tokens than you have. " + msg )
		else:
			raise forms.ValidationError("You must allocate all your tokens.")
		return cleaned_data


