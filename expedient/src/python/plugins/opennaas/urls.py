from django.conf.urls.defaults import *

urlpatterns = patterns('opennaas.views',
    url(r'^aggregate/create/$', 'aggregate_crud', name='opennaas_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='opennaas_aggregate_edit'),
    url(r'^aggregate/(?P<agg_id>\d+)/list_resources/$', 'list_resources', name='list_resources'),
)
