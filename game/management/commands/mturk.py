from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
from game.models import Participant, Experiment, Treatment
from amazon_credentials import *

def connect():
	mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
		      host=HOST)
	return mtc

def pay(amnt):
	return Price(amnt, currency_code='USD')

def create_hit():
	print "Creating a new hit"
	q = ExternalQuestion(external_url="http://perceptsconcepts.psych.indiana.edu/trustgame/portal/", frame_height=600)
	a = connect().create_hit(
		question=q,
		lifetime=60*60*24*2, # Two days
		max_assignments=50,
		title="Play a game with other MTurkers for research and earn bonuses",
		description="Exchange tokens with other Mturkers that are worth $0.002. By exchanging with others you can earn up to 3600 tokens or $7.20 in bonuses!",
		keywords=[ 'strategy', 'cognitive science', 'group behavior', 'economics', 'games', 'science', 'experiment', 'multiplayer', 'psychology', 'social science' ],
		reward=0.05,
		duration=60*60*12, # 12 hours
		approval_delay=60*60*24*7 # Five days
		)
	for i in a:
		print i.HITId

def get_all_reviewable_hits():
    page_size = 50
    mtc = connect()
    hits = mtc.get_reviewable_hits(page_size=page_size)
    total_pages = float(hits.TotalNumResults)/page_size
    int_total= int(total_pages)
    if(total_pages-int_total>0):
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
        hits.extend(temp_hits)
    return hits


def get_and_execute(function):
    data_hits = []
    print "Please choose a HIT"
    for p in Participant.objects.filter(group='mturk'):
	    if str(p.hitId) not in data_hits:
		    data_hits.append(str(p.hitId))
    print "These are from our data..."
    print data_hits
    mhits = []
    common = []
    for hit in get_all_reviewable_hits():
	    hitid =str(hit.HITId)
	    mhits.append(hitid)
	    if hitid in data_hits:
		    common.append(hitid)
    print "And these are from Amazon"
    print mhits
    print "The HITS that are both from amazon and from our data are:"
    print common
    ask = raw_input('Which one to use? ("all" to approve all.): ')
    if ask == "all":
	    for h in common:
		    function(h)
    elif not ask:
	    return False
    else:
	    function(common[int(ask)])
