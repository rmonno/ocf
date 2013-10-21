from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import simple
from django.forms.models import modelform_factory
from expedient.common.messaging.models import DatedMessage
from expedient.common.permissions.shortcuts import give_permission_to

from opennaas.models import OpennaasAggregate
import opennaas.geniv3 as gv3

import logging
logger = logging.getLogger("opennaas-views")

POST = DatedMessage.objects.post_message_to_user


def verify_connectivity(address, port):
    func_ = verify_connectivity.__name__
    logger.debug("%s address=%s, port=%s" % (func_, address, port,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))
    try:
        resp_ = geni3c_.getVersion()
        if geni3c_.isError(resp_):
            ecode_ = geni3c_.errorCode(resp_)
            return "An error occurred during communication with (OpenNaaS) AM: %d" % (ecode_,)

    except Exception as e:
        return "Unable to contact the (OpenNaaS) AM: %s" % (e,)

    return None


def list_available_resources(address, port):
    func_ = list_available_resources.__name__
    logger.debug("%s address=%s, port=%s" % (func_, address, port,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_, resources_ = None, []
    try:
        resp_ = geni3c_.listResources(credentials=[gv3.TEST_CREDENTIAL], available=True)
        if geni3c_.isError(resp_):
            err_ = "An error occurred during communication with (OpenNaaS) AM: %d" %\
                   (geni3c_.errorCode(resp_),)
        else:
            resources_ = gv3.decode_list_resources(resp_.get('value'))

    except Exception as e:
        err_ = "Unable to contact the (OpenNaaS) AM: %s" % (e,)

    return err_, resources_


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

            errors = verify_connectivity(info_.address, info_.port)
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
    errors, resources = list_available_resources(aggreg_.address, aggreg_.port)

    logger.debug("%s errors=%s, resources=%s" % (func_, errors, resources,))

    if not errors:
        return simple.direct_to_template(request, "default/list_resources.html",
                                         {'resources': resources, 'aggregate': aggreg_})

    POST(errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    return HttpResponseRedirect("/")


def get_ui_data(slice):
    logger.info("For now, return an empty list of nodes and links!")
    return {"nodes": [], "links": []}
