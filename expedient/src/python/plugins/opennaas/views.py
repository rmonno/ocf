from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage

from opennaas.models import OpennaasAggregate
import opennaas.geniv3 as gv3

import logging
logger = logging.getLogger("opennaas-views")

POST = DatedMessage.objects.post_message_to_user


def aggregate_crud(request, agg_id=None):
    logger.debug("Aggregation Identifier=%s" % (agg_id,))
    return generic_crud(request,
                        obj_id=agg_id,
                        model=OpennaasAggregate,
                        template_object_name="aggregate",
                        template="default/aggregate_crud.html",
                        redirect=lambda inst: reverse(
                            aggregate_add_resources, args=[inst.id]),
                        success_msg=lambda inst: \
                            "Successfully created/updated OpenNaaS Aggregate %s" % inst.name,)


def aggregate_add_resources(request, agg_id):
    logger.debug("Aggregation Identifier=%s" % (agg_id))
    aggregate = get_object_or_404(OpennaasAggregate, id=agg_id)

    if aggregate.geni3c != None:
        POST("This aggregate has already configured with a GENIv3Client!",
             user=request.user,
             msg_type=DatedMessage.TYPE_ERROR,)
        return HttpResponseRedirect("/")

    aggregate.geni3c = gv3.GENI3Client(aggregate.address, aggregate.port)
    logger.debug("Geniv3Client successfully init...")

    try:
        resp_ = aggregate.geni3c.getVersion()
        if aggregate.geni3c.isError(resp_):
            ecode_ = aggregate.geni3c.errorCode(resp_)
            POST("An error occurred during communication with (OpenNaaS) AM: %d" % (ecode_,),
                 user=request.user,
                 msg_type=DatedMessage.TYPE_ERROR,)
            return HttpResponseRedirect("/")

    except Exception as e:
        POST("Unable to contact the (OpenNaaS) AM: %s" % (e,),
             user=request.user,
             msg_type=DatedMessage.TYPE_ERROR,)
        return HttpResponseRedirect("/")


    return HttpResponseRedirect("/")


def get_ui_data(slice):
    logger.info("For now, return an empty list of nodes and links!")
    return {"nodes": [], "links": []}
