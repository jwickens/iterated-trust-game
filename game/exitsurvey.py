from django.db import models
from django.forms import ModelForm, RadioSelect, Form, HiddenInput, IntegerField 

def choice_list(pre=None, start=0, end=21, final=None, empty_label=False):
	if pre:
		arr = [pre]
	else:
		arr = []
	for i in range(start, end):
		arr.append(str(i))
	if final:
		arr.append(final)
	if empty_label:
		return [(x,'') for x in arr]
	else:
		return [(x,x) for x in arr]

PREV_EXP_CHOICES = choice_list('None', 1, 20, '20+')
YN = [('y','Yes'), ('n','No')]
TOKENS = choice_list()
RETURNS = choice_list(end=61)
SCALE = choice_list(end=11)
SCALE2 = choice_list(start=1, end=8, empty_label=True)
SCALE3 = choice_list(start=1, end=6, empty_label=True)

class ExitSurvey(models.Model):
	prev_exp = models.CharField(max_length=4, verbose_name='1. How many previous experiments have you participated in?', choices=PREV_EXP_CHOICES)
	clarity = models.CharField(max_length=4, verbose_name='2. Were the instructions clear?', choices=YN)
	questions = models.TextField(blank=True, verbose_name='3. Do you have any questions or commments?')
	problems = models.TextField(blank=True, verbose_name='4. Did you notice any bugs or errors in the software? Please describe them here.')
	tech = models.CharField(max_length=2, verbose_name='5. On a scale of 0 to 10, how much did difficulties with the interface negatively affect your experience?', choices=SCALE)
	educ = models.CharField(max_length=2,
		verbose_name="6. How many years of education have you had? (If you live in the USA, a High School Degree is normally 12 years, College Freshman is 13 years, etc.)", 
		choices=choice_list(end=25,final="Prefer not to respond"))
	gender = models.CharField(max_length=20, verbose_name="8. What is your gender?", choices=[('m','male'), ('f','female'), ('o','other'), ('nr','prefer not to respond')])
	surveyer = models.IntegerField()

class MACHIV(models.Model):
	mach1 = models.CharField(max_length=20, verbose_name="Never tell anyone the real reason you did something unless it is useful to do so.", choices=SCALE2)
	mach2 = models.CharField(max_length=20, verbose_name="The best way to handle people is to tell them what they want to hear.", choices=SCALE2)
	mach3 = models.CharField(max_length=20, verbose_name="One should take action only when sure it is morally right.", choices=SCALE2)
	mach4 = models.CharField(max_length=20, verbose_name="Most people are basically good and kind.", choices=SCALE2)
	mach5 = models.CharField(max_length=20, verbose_name="It is safest to assume that all people have a vicious streak and it will come out when they are given a chance.", choices=SCALE2)
	mach6 = models.CharField(max_length=20, verbose_name="Honesty is the best policy in all cases.", choices=SCALE2)
	mach7 = models.CharField(max_length=20, verbose_name="There is no excuse for lying to someone else.", choices=SCALE2)
	mach8 = models.CharField(max_length=20, verbose_name="Generally speaking, people won't work hard unless they're forced to do so.", choices=SCALE2)
	mach9 = models.CharField(max_length=20, verbose_name="All in all, it is better to be humble and honest than to be important and dishonest.", choices=SCALE2)
	mach10 = models.CharField(max_length=20,
		verbose_name="When you ask someone to do something for you, it is best to give the real reasons for wanting it rather than giving reasons which carry more weight.", choices=SCALE2)
	mach11 = models.CharField(max_length=20, verbose_name="Most people who get ahead in the world lead clean, moral lives.", choices=SCALE2)
	mach12 = models.CharField(max_length=20, verbose_name="Anyone who completely trusts anyone else is asking for trouble.", choices=SCALE2)
	mach13 = models.CharField(max_length=20, verbose_name="The biggest difference between most criminals and other people is that the criminals are stupid enough to get caught.", choices=SCALE2)
	mach14 = models.CharField(max_length=20, verbose_name="Most people are brave.", choices=SCALE2)
	mach15 = models.CharField(max_length=20, verbose_name="It is wise to flatter important people.", choices=SCALE2)
	mach16 = models.CharField(max_length=20, verbose_name="It is possible to be good in all respects.", choices=SCALE2)
	mach17 = models.CharField(max_length=20, verbose_name="P.T. Barnum was wrong when he said that there's a sucker born every minute.", choices=SCALE2)
	mach18 = models.CharField(max_length=20, verbose_name="It is hard to get ahead without cutting corners here and there.", choices=SCALE2)
	mach19 = models.CharField(max_length=20, verbose_name="People suffering from incurable diseases should have the choice of being put painlessly to death.", choices=SCALE2)
	mach20 = models.CharField(max_length=20, verbose_name="Most people forget more easily the death of their parents than the loss of their property.", choices=SCALE2)
	score = models.IntegerField(null=True)

	def create_score(self):
		score = 20
		#Scored Normally
		for i in [1,2,5,8,12,13,15,18,19,20]:
			score += int(getattr(self,'mach'+str(i)))

		#Reverse Scored
		for i in [3,4,6,7,9,10,11,14,16,17]:
			score += 8-int(getattr(self,'mach'+str(i)))
		self.score = score
		self.save()
		return score

class BIG5(models.Model):
	big0 = models.CharField(max_length=20, verbose_name="...is reserved", choices=SCALE3)
	big1 = models.CharField(max_length=20, verbose_name="...is generally trusting", choices=SCALE3)
	big2 = models.CharField(max_length=20, verbose_name="...tends to be lazy", choices=SCALE3)
	big3 = models.CharField(max_length=20, verbose_name="...is relaxed, handles stress well", choices=SCALE3)
	big4 = models.CharField(max_length=20, verbose_name="...has few artistic interests", choices=SCALE3)
	big5 = models.CharField(max_length=20, verbose_name="...is outgoing, sociable", choices=SCALE3)
	big6 = models.CharField(max_length=20, verbose_name="...tends to find fault", choices=SCALE3)
	big7 = models.CharField(max_length=20, verbose_name="...does a thorough job", choices=SCALE3)
	big8 = models.CharField(max_length=20, verbose_name="...gets nervous easily", choices=SCALE3)
	big9 = models.CharField(max_length=20, verbose_name="...has an active imagination", choices=SCALE3)
	
	extroversion = models.IntegerField(null=True)
	agreeableness = models.IntegerField(null=True)
	conscientiousness = models.IntegerField(null=True)
	neuroticism = models.IntegerField(null=True)
	openness = models.IntegerField(null=True)

	def create_score(self):
		self.extroversion = 6 - int(self.big0) + int(self.big5)
		self.agreeableness = int(self.big1) + 6 -int(self.big6)
		self.conscientiousness = 6 - int(self.big2) + int(self.big7)
		self.neuroticism = 6 - int(self.big3) + int(self.big8)
		self.openness = 6 - int(self.big4) + int(self.big9)
		self.save()


def widgetize(fields, cls):
	widgets = {}
	for i in fields:
		widgets[i] = cls
	return widgets

class SurveyForm(ModelForm):
	class Meta:
		model = ExitSurvey
		widgets = {'surveyer' : HiddenInput }

	def __init__(self, p_num, *args, **kwargs):
		initial = kwargs.get('initial', {})
		initial['surveyer'] = p_num
		kwargs['initial'] = initial
		super(SurveyForm,self).__init__(*args,**kwargs)

class MACHIVForm(ModelForm):
	class Meta:
		model = MACHIV
		fields = tuple([ 'mach' + str(i) for i in range(1,21)])
		widgets = widgetize(fields, RadioSelect)

class BIG5Form(ModelForm):
	class Meta:
		model = BIG5
		fields = tuple([ 'big' + str(i) for i in range(0,10)])
		widgets = widgetize(fields, RadioSelect)

