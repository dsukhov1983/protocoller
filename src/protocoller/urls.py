from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = 'perfect404.views.page_not_found'

urlpatterns = patterns(
    'protocoller.miner.views',

    (r'^$', 'protocols_view', {}, 'main'),
    (r'^index.html', 'protocols_view'),

    (r'^calendar/$', 'calendar_view', {}, 'calendar'),
    (r'^calendar/(?P<year>\d{4})-(?P<month>\d+)/$', 'calendar_month_view', {}, 'calendar_month'),

    (r'^protocols/$', 'protocols_view', {}, 'protocols'),
    (r'^protocols/(?P<year>\d{4})-(?P<month>\d+)/$', 'protocols_month_view', {}, 'protocols_month'),
    (r'^protocol/(?P<comp_id>\d+)$', 'protocol', {}, 'protocol'),
    (r'^protocol/(?P<comp_id>\d+)/groups$', 'protocol_by_groups',
        {}, 'protocol_by_groups'),

    (r'^events/$', 'events_view', {}, 'events'),
    (r'^events/add/$', 'edit_event_view', {}, 'add_event'),
    (r'^event/(?P<event_id>\d+)/edit/$', 'edit_event_view', {},
     'edit_event'),
    (r'^event/(?P<event_id>\d+)/$', 'event_view', {}, 'event'),
    (r'^event/(?P<event_id>\d+)/registration/$', 'register_on_event_view',
     {}, 'event_registration'),
    (r'^event/(?P<event_id>\d+)/subscribe/(?P<reg_id>\d+)/$',
     'subscribe_on_event_view', {}, 'event_subscribe'),
    (r'^event/(?P<event_id>\d+)/unsubscribe/(?P<reg_id>\d+)/$',
     'unsubscribe_from_event_view', {}, 'event_unsubscribe'),
    (r'^event/(?P<event_id>\d+)/get/reg_info/$', 'get_reg_info_view', {},
     'download_reg_info'),
    (r'^events/past/$', 'past_events_view', {}, 'past_events'),
    (r'^events/future/$', 'future_events_view', {}, 'future_events'),


    (r'^places/$', 'places_view', {}, 'places'),
    (r'^places/add/$', 'edit_place_view', {}, 'add_place'),
    (r'^place/(?P<id>[\w\d\-]+)/$', 'place_view', {}, 'place'),
    (r'^place/(?P<id>[\w\d\-]+)/edit/$', 'edit_place_view', {}, 'edit_place'),

    (r'^persons/$', 'persons_view', {}, 'persons'),
    (r'^person/(?P<person_id>\d+)/$', 'person_view', {}, 'person'),

    (r'^search$', 'search_view', {}, 'search'),
    (r'^compare$', 'compare_view', {}, 'compare'),
    (r'^person_fb/(?P<person>\d+)$', 'feedback_person', {}, 'feedback_person'),

    (r'^login/$', 'login_view', {}, 'login'),
    (r'^logout/$', 'logout_view', {}, 'logout'),
    (r'^about/$', 'about'),

    (r'^activity/$', 'activity_view'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', include(admin.site.urls)),
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
    url(r'^markitup/', include('markitup.urls')),  # markitup
    (r'^comments/', include('django.contrib.comments.urls')),  # comments
    (r'^sentry/', include('sentry.web.urls')),  # sentry
    )


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns(
         '',
         (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
              {'document_root': '/home/quoter/www/protocoller/media/'}),
          )
