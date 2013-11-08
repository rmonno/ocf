from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
import opennaas.geniv3_commands as gv3_cmds

import logging
logger = logging.getLogger("opennaas-models")


class OpennaasAggregate(Aggregate):
    information = "An aggregate-plugin to manage OpenNaaS resources"\
        " For now, only Wonesys ROADMs devices are supported."

    class Meta:
        verbose_name = "OpenNaaS Aggregate"

    address = models.TextField(default='127.0.0.1',
                               help_text='Address of the (OpenNaaS) Aggregate Manager',)

    port = models.PositiveIntegerField(default='8001',
                                       help_text='Port of the (OpenNaaS) Aggregate Manager',)

    def start_slice(self, slice):
        func_ = OpennaasAggregate.start_slice.__name__
        super(OpennaasAggregate, self).start_slice(slice)
        logger.debug("%s slice=%s, address=%s, port=%d" %
                     (func_, slice, self.address, self.port,))

        errors = gv3_cmds.perform_operation(self.address, self.port,
                                            slice.name, 'geni_start')
        if errors:
            raise Exception(errors)

    def stop_slice(self, slice):
        func_ = OpennaasAggregate.stop_slice.__name__
        super(OpennaasAggregate, self).stop_slice(slice)
        logger.debug("%s slice=%s, address=%s, port=%d" %
                     (func_, slice, self.address, self.port,))

        errors = gv3_cmds.perform_operation(self.address, self.port,
                                            slice.name, 'geni_stop')
        if errors:
            raise Exception(errors)
