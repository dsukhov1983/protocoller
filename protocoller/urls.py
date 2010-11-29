from django.conf.urls.defaults import *
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'protocoller.miner.views',    
    # Example:
    (r'^$', 'comp_list_view'),
    (r'^index.html$', 'comp_list_view'),
    (r'^comp/(?P<year>\d+)$', 'comp_list_view'),
    (r'^comp/(?P<year>\d+)/(?P<month>\d+)$',
     'comp_list_view'),
    (r'^protocol/(?P<comp_id>\d+)$', 'protocol', {}, 'protocol'),
    (r'^protocol/(?P<comp_id>\d+)/groups$', 'protocol_by_groups',
     {}, 'protocol_by_groups'),
    (r'^person/(?P<person_id>\d+)/results$', 'person_results',
     {}, 'person_results'),
    (r'^search$', 'search'),
    (r'^compare$', 'compare', {}, 'compare'),
    (r'^compare/query/add/(?P<add>\d+)$', 'compare', {}, 'compare_add'),
    (r'^compare/query/del/(?P<delete>\d+)$', 'compare', {}, 'compare_del'),
    (r'^do_compare$', 'do_compare'),
    (r'^person_fb/(?P<person>\d+)$', 'feedback_person',
     {}, 'feedback_person'),

    (r'^about$', 'about'),
    
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
  

)

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$',
                             'django.views.static.serve',
                             {'document_root': '/home/quoter/devel/protocoller/'}),
                            )
