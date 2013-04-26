import time

import datetime
from openflow.optin_manager.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from openflow.optin_manager.sfa.util.defaultdict import defaultdict
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from openflow.optin_manager.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from openflow.optin_manager.sfa.util.cache import Cache

from openflow.optin_manager.sfa.rspecs.version_manager import VersionManager
from openflow.optin_manager.sfa.rspecs.rspec import RSpec

from openflow.optin_manager.sfa.OFAggregate import OFAggregate
from openflow.optin_manager.sfa.OFShell import OFShell

class OFSfaDriver:

	def __init__ (self, config=None):
		self.aggregate = OFAggregate()
		self.shell = OFShell()

	def list_resources (self,slice_urn=None, slice_leaf=None, creds=[], options={},):

		version_manager = VersionManager()
		rspec_version = 'OcfOf'
        	version_string = "rspec_%s" % (rspec_version)
                if slice_urn:
                    options['slice_urn'] = slice_urn
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options)
       		return rspec

	def crud_slice (self,slice_urn,authority,creds=None, action=None):

                try:
		    if action == 'start_slice':
		        self.shell.StartSlice()
		    elif action == 'stop_slice':
			self.shell.StopSlice()
	       	    elif action == 'delete_slice':
			self.shell.DeleteSlice()
		    elif action == 'reset_slice':
			self.shell.RebootSlice()

                    return 1

                except Exception as e:
                        raise RecordNotFound(slice_leaf)
	

        def create_sliver (self,slice_leaf,authority,rspec_string, users, options):
                rspec = RSpec(rspec_string,'OcfOf')
                requested_attributes = rspec.version.get_slice_attributes()
		projectName = authority
		sliceName = slice_leaf
		self.shell.CreateSliver(requested_attributes,slice_leaf,projectName)
	        options['slivers'] = requested_attributes
            	
		return self.aggregate.get_rspec(slice_leaf=slice_leaf,projectName=projectName,version=rspec.version,options=options)
	
	def sliver_status(self,slice_leaf,authority,creds,options):
		result = OFShell.SliverStatus(slice_urn)
		return result
			

		
	

