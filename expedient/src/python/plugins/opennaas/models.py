from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate

import logging
logger = logging.getLogger("opennaas-models")


class OpennaasAggregate(Aggregate):
    information = "An aggregate to manage OpenNaas resources"\
        " For now, only Wonesys ROADMs devices are supported."

    class Meta:
        verbose_name = "OpenNaas Aggregate"

    test_field = models.TextField(default='only a test',
                                  help_text='write what you want...',)

    def start_slice(self, slice):
        super(OpennaasAggregate, self).start_slice(slice)
        logger.debug("Started slice")

    def stop_slice(self, slice):
        super(OpennaasAggregate, self).stop_slice(slice)
        logger.debug("Stopped slice")
