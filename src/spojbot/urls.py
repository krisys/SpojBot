from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'bot.views.index', name='index'),
    url(r'^spoj$', 'bot.views.spoj', name='spoj'),
    url(r'^settings$', 'bot.views.config', name='config'),
    url(r'^group/create$', 'bot.views.create_group', name='create_group'),
    url(r'^group/(?P<id>\d+)/$', 'bot.views.view_group', name='view_group'),
    url(r'^group/(?P<id>\d+)/members$', 'bot.views.view_group_members', name='view_group_members'),
    url(r'^delete_member/(?P<id>\d+)/$', 'bot.views.delete_member', name='delete_member'),
    url(r'^delete_group/$', 'bot.views.delete_group', name='delete_group'),
    url(r'^leave_group/$', 'bot.views.leave_group', name='leave_group'),
    url(r'^suggest_problem/$', 'bot.views.suggest_problem', name='suggest_problem'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/'}),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)
