from django.http import HttpResponseServerError

import logging
logger = logging.getLogger("sshaggregate-views")


def aggregate_crud(request, agg_id=None):
    logger.error("Not implemented!")
    return HttpResponseServerError("Not implemented yet!")


def get_ui_data(slice):
    logger.info("For now, return an empty list of nodes and links!")
    return {"nodes": [], "links": []}
