from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate

import logging
logger = logging.getLogger("opennaas-models")


class OpennaasAggregate(Aggregate):
    information = "An aggregate to manage OpenNaas resources"\
        " For now, only Wonesys ROADMs devices are supported."

    class Meta:
        verbose_name = "OpenNaas Aggregate"

    address = models.TextField(default='127.0.0.1',
                               help_text='Address of the (OpenNaaS) Aggregate Manager',)

    port = models.PositiveIntegerField(default='8001',
                                       help_text='Port of the (OpenNaaS) Aggregate Manager',)

    geni3c = None

    def start_slice(self, slice):
        super(OpennaasAggregate, self).start_slice(slice)
        logger.debug("Started slice")

    def stop_slice(self, slice):
        super(OpennaasAggregate, self).stop_slice(slice)
        logger.debug("Stopped slice")
