from django.http import HttpResponseServerError
from django.core.urlresolvers import reverse
from expedient.common.utils.views import generic_crud

from opennaas.models import OpennaasAggregate

import logging
logger = logging.getLogger("sshaggregate-views")


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
    return HttpResponseServerError("Not implemented yet!")


def get_ui_data(slice):
    logger.info("For now, return an empty list of nodes and links!")
    return {"nodes": [], "links": []}
