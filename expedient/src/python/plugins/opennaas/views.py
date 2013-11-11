from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import simple
from django.forms.models import modelform_factory
from django.db.models import Q
from expedient.common.messaging.models import DatedMessage
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.utils.plugins.resources.node import Node
from expedient.common.utils.plugins.resources.link import Link
from expedient.clearinghouse.slice.models import Slice

from opennaas.models import OpennaasAggregate
from opennaas.forms import AllocateForm
import opennaas.geniv3_commands as gv3_cmds

import logging
logger = logging.getLogger("opennaas-views")

POST = DatedMessage.objects.post_message_to_user


def aggregate_crud(request, agg_id=None):
    func_ = aggregate_crud.__name__
    logger.debug("%s method=%s, id=%s" % (func_, request.method, agg_id,))

    aggreg_ = None
    if agg_id:
        aggreg_ = get_object_or_404(OpennaasAggregate, id=agg_id)
    logger.debug("%s Aggregate=%s" % (func_, aggreg_,))

    AGGModelForm = modelform_factory(OpennaasAggregate)

    if request.method == 'GET':
        agg_form_ = AGGModelForm(instance=aggreg_)
        return simple.direct_to_template(request, "default/aggregate_crud.html",
                                         {'form': agg_form_, 'aggregate': aggreg_})
    elif request.method == 'POST':
        agg_form_ = AGGModelForm(data=request.POST, instance=aggreg_)

        if agg_form_.is_valid():
            info_ = agg_form_.save(commit=False)
            logger.debug("%s info=%s" % (func_, info_,))

            errors = gv3_cmds.verify_connectivity(info_.address, info_.port)
            if not errors:
                info_.save()
                agg_form_.save_m2m()
                give_permission_to('can_use_aggregate', info_,
                                   request.user, can_delegate=True)
                give_permission_to('can_edit_aggregate', info_,
                                   request.user, can_delegate=True)

                POST("Successfully created/updated aggregate %s" % info_.name,
                     user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
            else:
                POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
                return simple.direct_to_template(request, "default/aggregate_crud.html",
                                                 {'form': agg_form_, 'aggregate': aggreg_})
    else:
        POST("%s Not Allowed method: %s" % (func_, request.method,),
             user=request.user, msg_type=DatedMessage.TYPE_ERROR,)

    return HttpResponseRedirect("/")


def list_resources(request, agg_id):
    func_ = list_resources.__name__
    logger.debug("%s method=%s, id=%s" % (func_, request.method, agg_id,))

    aggreg_ = get_object_or_404(OpennaasAggregate, id=agg_id)
    errors, resources = gv3_cmds.list_available_resources(aggreg_.address, aggreg_.port)

    logger.debug("%s errors=%s, resources=%s" % (func_, errors, resources,))

    if not errors:
        set_ = set()
        [set_.add((r_['name'], r_['type'], r_['endpoint'],)) for r_ in resources]

        logger.debug("%s set=%s" % (func_, set_,))

        resources_ = [{'name': r_[0], 'type': r_[1], 'endpoint': r_[2]} for r_ in set_]

        return simple.direct_to_template(request, "default/list_resources.html",
                                         {'resources': resources_, 'aggregate': aggreg_,
                                          'resource_len': len(resources)})

    POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


def list_labels(request, agg_id, name, type, endpoint):
    func_ = list_labels.__name__
    logger.debug("%s method=%s, id=%s, name=%s, type=%s, endpoint=%s" %\
                 (func_, request.method, agg_id, name, type, endpoint,))

    aggreg_ = get_object_or_404(OpennaasAggregate, id=agg_id)
    errors, resources = gv3_cmds.list_available_resources(aggreg_.address, aggreg_.port)

    logger.debug("%s errors=%s, resources=%s" % (func_, errors, resources,))

    if not errors:
        labels_ = [r_ for r_ in resources\
                   if r_['name'] == name and r_['type'] == type and r_['endpoint'] == endpoint]

        logger.debug("%s labels=%s" % (func_, labels_,))

        return simple.direct_to_template(request, "default/list_labels.html",
                                         {'resources': labels_, 'aggregate': aggreg_,
                                          'resource_len': len(labels_)})

    POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


def describe(request, slice_id, agg_id):
    func_ = describe.__name__
    logger.debug("%s method=%s, slice=%s, agg=%s" % (func_, request.method, slice_id, agg_id,))

    slice_ = get_object_or_404(Slice, id=slice_id)
    opns_agg_ = get_object_or_404(OpennaasAggregate, id=agg_id)
    errors, resources = gv3_cmds.status_resources(opns_agg_.address, opns_agg_.port, slice_.name)

    logger.debug("%s errors=%s, resources=%s" % (func_, errors, resources,))

    if not errors:
        return simple.direct_to_template(request, "default/describe_resources.html",
                                         {'resources': resources, 'aggregate': opns_agg_,
                                          'resource_len': len(resources), 'slice': slice_,
                                          'back': "/slice/detail/%s" % slice_.id})

    POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


def allocate(request, slice_id, agg_id):
    func_ = allocate.__name__
    logger.debug("%s method=%s, slice=%s, agg=%s" % (func_, request.method, slice_id, agg_id,))

    slice_ = get_object_or_404(Slice, id=slice_id)
    opns_agg_ = get_object_or_404(OpennaasAggregate, id=agg_id)

    if request.method == 'GET':
        alloc_form_ = AllocateForm()
        return simple.direct_to_template(request, "default/allocate_resources.html",
                                         {'form': alloc_form_, 'slice': slice_,
                                          'aggregate': opns_agg_})
    elif request.method == 'POST':
        alloc_form_ = AllocateForm(data=request.POST)
        if alloc_form_.is_valid():
            info_ = {'name': alloc_form_.cleaned_data['name'],
                     'type': alloc_form_.cleaned_data['type'],
                     'in_ep': alloc_form_.cleaned_data['ingress_endpoint'],
                     'in_lab': alloc_form_.cleaned_data['ingress_label'],
                     'out_ep': alloc_form_.cleaned_data['egress_endpoint'],
                     'out_lab': alloc_form_.cleaned_data['egress_label']}
            errors = gv3_cmds.allocate_resource(opns_agg_.address, opns_agg_.port,
                                                slice_.name, info_)
            if not errors:
                POST("Successfully allocated the resource",
                     user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
                return HttpResponseRedirect("/slice/detail/%s" % slice_.id)

            else:
                POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
                return simple.direct_to_template(request, "default/allocate_resources.html",
                                                 {'form': alloc_form_, 'slice': slice_,
                                                  'aggregate': opns_agg_})
        else:
            POST('AllocateForm is NOT valid!', user=request.user, msg_type=DatedMessage.TYPE_ERROR,)

    else:
        POST("%s Not Allowed method: %s" % (func_, request.method,),
             user=request.user, msg_type=DatedMessage.TYPE_ERROR,)

    return HttpResponseRedirect("/")


def delete(request, slice_id, agg_id):
    func_ = delete.__name__
    logger.debug("%s method=%s, slice=%s, agg=%s" % (func_, request.method, slice_id, agg_id,))

    slice_ = get_object_or_404(Slice, id=slice_id)
    opns_agg_ = get_object_or_404(OpennaasAggregate, id=agg_id)

    errors = gv3_cmds.delete_slice(opns_agg_.address, opns_agg_.port, slice_.name)
    if not errors:
        POST("Successfully deleted all resources belonging to %s" % slice_.name,
             user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
        return HttpResponseRedirect("/slice/detail/%s" % slice_.id)

    POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


def renew(request):
    func_ = renew.__name__
    logger.debug("%s method=%s" % (func_, request.method,))

    POST('Not implemented yet!', user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


# aggregate management
def get_opennaas_roadm_aggregates(slice):
    aggs_filter = Q(leaf_name=OpennaasAggregate.__name__.lower())
    return slice.aggregates.filter(aggs_filter)


def get_opennaas_roadm_id(resources, name):
    for r in resources:
        if r.get('name') == name:
            return r.get('id')

    return None


def get_ui_data(slice):
    func_ = get_ui_data.__name__
    logger.debug("%s retrieving info for %s" % (func_, slice.name))

    nodes_, links_ = ([], [])

    for aggreg_ in get_opennaas_roadm_aggregates(slice):
        opns_agg_ = get_object_or_404(OpennaasAggregate, id=aggreg_.pk)
        errors, resources = gv3_cmds.status_resources(opns_agg_.address, opns_agg_.port, slice.name)

        logger.debug("%s errors=%s, resources=%s" % (func_, errors, resources,))

        if not errors:
            for r_ in resources:
                nodes_.append(Node(name=r_.get('name'), value=r_.get('id'),
                                   description='how to read = name:endpoint:label',
                                   type=r_.get('type'), image='switch-tiny.png', aggregate=aggreg_))

                if r_.get('ingress') != None:
                    links_.append(Link(source=str(r_.get('id')),
                                       target=str(get_opennaas_roadm_id(resources, r_.get('ingress'))),
                                       value=r_.get('ingress') + '-' + r_.get('name')))

                elif r_.get('egress') != None:
                    links_.append(Link(source=str(r_.get('id')),
                                       target=str(get_opennaas_roadm_id(resources, r_.get('egress'))),
                                       value=r_.get('name') + '-' + r_.get('egress')))

    logger.debug("%s retrieved info nodes=%s, links=%s" % (func_, nodes_, links_,))
    return {"nodes": nodes_, "links": links_}
