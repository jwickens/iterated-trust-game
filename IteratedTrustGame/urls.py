from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()
handler500 = 'game.views.error500'
handler404 = 'game.views.error404'
urlpatterns = patterns('',
		url(r'^', include('game.urls')),
		#url(r'^admin/', include(admin.site.urls)),
    # Examples:
    # url(r'^$', 'IteratedTrustGame.views.home', name='home'),
    # url(r'^IteratedTrustGame/', include('IteratedTrustGame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)
urlpatterns += staticfiles_urlpatterns()
