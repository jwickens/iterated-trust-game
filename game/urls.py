from django.conf.urls import patterns, include, url
from game import views
from game import ajax

urlpatterns = patterns('',
    ## These use the html_base
    url(r'^$', views.portal, name='index'),
    url(r'portal/$', views.portal, name='portal'),
    url(r'mturk/(?P<workerId>.*)$', views.mturk, name='mturk'),
    url(r'coop/$', views.coop, name='coop'),
    url(r'consent/$', views.consent, name='consent'),
    url(r'instructions/$', views.instructions, name='instructions'),
    url(r'practice/$', views.practice, name='practice'),
    url(r'pretest/$', views.pretest, name='pretest'),
    ## These use the client_base template to do check-ins
    url(r'start/$', views.start, name='start'),
    url(r'game/$', views.game , name='game'),
    url(r'survey/$', views.survey, name='survey'),
    url(r'end/$', views.end, name='end'),
    ## Other
    url(r'basic/$', views.basic, name='basic'),
    url(r'error/$', views.error, name='error'),

   ##AJAX
    url(r'json/queue/(?P<p_id>\d+)/(?P<focus>.*)/$', ajax.queue, name='queue'),
    url(r'json/checkin/(?P<p_id>\d+)/(?P<game_state>.*)/$', ajax.checkin, name='checkin'),
    url(r'json/loadscreen/(?P<p_id>\d+)/$', ajax.loadscreen, name='loadscreen'),
    url(r'json/loadform/(?P<p_id>\d+)/$', ajax.loadform, name='loadform'),
    url(r'json/loadhistory/(?P<p_id>\d+)/(?P<turn_num>\d+)/$', ajax.loadhistory, name='loadhistory'),
    url(r'json/loadhistory/(?P<p_id>\d+)/$', ajax.loadhistory, name='loadhistory'),
    url(r'json/submit/(?P<p_id>\d+)/$', ajax.submit, name='submit'),
    url(r'json/verify/(?P<p_id>\d+)/$', ajax.verify, name='verify'),
    #url(r'json/checkin/$', ajax.checkin, name='checkin')
   )

