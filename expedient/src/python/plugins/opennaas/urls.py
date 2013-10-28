from django.conf.urls.defaults import *

urlpatterns = patterns('opennaas.views',
    url(r'^aggregate/create/$', 'aggregate_crud', name='opennaas_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='opennaas_aggregate_edit'),
    url(r'^aggregate/(?P<agg_id>\d+)/list_resources/$', 'list_resources', name='list_resources'),

    url(r'opennaas/describe/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'describe', name='describe'),
    url(r'^opennaas/allocate/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'allocate', name='allocate'),
    url(r'^opennaas/delete/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'delete', name='delete'),
    url(r'^opennaas/renew/$', 'renew', name='renew'),
)
