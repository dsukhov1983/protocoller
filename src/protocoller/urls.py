from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    'protocoller.miner.views',    

    (r'^$', 'main_view', {}, 'main'),
    (r'^index.html$', 'main_view'),
    

    (r'^events/$', 'events_view', {}, 'events'),
    (r'^events/add/$', 'edit_event_view', {}, 'add_event'),
    (r'^event/(?P<event_id>\d+)/edit/$', 'edit_event_view', {}, 
     'edit_event'),
    (r'^event/(?P<event_id>\d+)/$', 'event_view', {}, 'event'),
    (r'^event/(?P<event_id>\d+)/registration/$', 'register_on_event_view', 
     {}, 'event_registration'),
    (r'^event/(?P<event_id>\d+)/subscribe/(?P<reg_id>)/$', 
     'subscribe_on_event_view', {}, 'event_subscribe'),
    (r'^event/(?P<event_id>\d+)/unsubscribe/(?P<reg_id>)/$', 
     'unsubscribe_from_event_view', {}, 'event_unsubscribe'),
    (r'^event/(?P<event_id>\d+)/get/reg_info', 'get_reg_info_view', {}, 
     'download_reg_info'),
    
    (r'^protocols/$', 'comp_list_view'),
    (r'^protocol/(?P<comp_id>\d+)$', 'protocol', {}, 'protocol'),
    (r'^protocol/(?P<comp_id>\d+)/groups$', 'protocol_by_groups',
     {}, 'protocol_by_groups'),
    
    (r'^places/$', 'places_view', {}, 'places'),
    (r'^places/add/$', 'edit_place_view', {}, 'add_place'),
    (r'^place/(?P<id>[\w\d\-]+)/$', 'place_view', {}, 'place'),
    (r'^place/(?P<id>[\w\d\-]+)/edit/$', 'edit_place_view', {}, 'edit_place'),
    
    
    (r'^sportsmen/$', 'sportsmen_view'),
    (r'^comp/(?P<year>\d+)$', 'comp_list_view'),
    (r'^comp/(?P<year>\d+)/(?P<month>\d+)$',  'comp_list_view'),
    (r'^person/(?P<person_id>\d+)/results$', 'person_results',
     {}, 'person_results'),
    (r'^search$', 'search'),
    (r'^compare$', 'compare', {}, 'compare'),
    (r'^compare/query/add/(?P<add>\d+)$', 'compare', {}, 'compare_add'),
    (r'^compare/query/del/(?P<delete>\d+)$', 'compare', {}, 'compare_del'),
    (r'^do_compare$', 'do_compare'),
    (r'^person_fb/(?P<person>\d+)$', 'feedback_person',
     {}, 'feedback_person'),
    
    (r'^login/$', 'login_view', {}, 'login'),
    (r'^logout/$', 'logout_view', {}, 'logout'),
    (r'^about$', 'about'),
        
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)


urlpatterns += patterns(
    '',
    (r'^accounts/openid/$', 'socialauth.views.openid_login', {}, 'socialauth_openid_login'),
    (r'^accounts/openid/complete/$', 'openid_consumer.views.complete', {},
     'socialauth_openid_complete'),
    (r'^accounts/openid/done/$', 'socialauth.views.openid_done', {}, 'socialauth_openid_done'),
    (r'^accounts/openid/signout/$', 'openid_consumer.views.signout', {},
     'socialauth_openid_sognout'),
    (r'^accounts/', include('registration.urls')),
    
    #markitup
    url(r'^markitup/', include('markitup.urls'))
    )


if settings.DEBUG:
    urlpatterns += patterns(
          '',
          (r'^media/(?P<path>.*)$',
          'django.views.static.serve',
               {'document_root': '/home/quoter/www/protocoller/media/'}),
           )

