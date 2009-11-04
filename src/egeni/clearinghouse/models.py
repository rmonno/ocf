from django.db import models
from django.db.models import permalink
from django.forms import ModelForm
from django.contrib.auth.models import User
import egeni_api
import plc_api

class AggregateManager(models.Model):
    '''An Aggregate Manager'''
    
    TYPE_OF = 'OF'
    TYPE_PL = 'PL'
    
    AM_TYPE_CHOICES={TYPE_OF: 'E-GENI Aggregate',
                     TYPE_PL: 'PlanetLab Aggregate',
                     }

    # @ivar name: The name of the aggregate manager. Must be unique 
    name = models.CharField(max_length=200, unique=True)
    
    # @ivar url: Location where the aggregate manager can be reached
    url = models.URLField('Aggregate Manager URL', unique=True, verify_exists=False)
    
    # @ivar type: Aggregate Type: OF or PL
    type = models.CharField(max_length=20, choices=AM_TYPE_CHOICES.items())
    
    # @ivar remote_node_set: nodes that this AM connects to that are not under its control
    remote_node_set = models.ManyToManyField("Node", related_name='remote_am_set',
                                             blank=True, null=True)

    # @ivar local_node_set: nodes that this AM connects to that are under its control
    
    # @ivar connected_node_set: nodes that this AM connects to that are or are not under its control
    connected_node_set = models.ManyToManyField("Node",
                                                related_name='connected_am_set',
                                                blank=True, null=True)
    
    # @ivar extra_context: Aggregate specific information
    extra_context = models.TextField(blank=True, null=True)
    
    # @ivar owner is the creator of the aggregate manager
    owner = models.ForeignKey(User)
    
    def get_absolute_url(self):
        return ('am_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def __unicode__(self):
        return AggregateManager.AM_TYPE_CHOICES[self.type] + ' ' + self.name + ' at ' + self.url
    
    def get_local_nodes(self):
        return self.local_node_set.all()
    
    def updateRSpec(self):
        print "Update RSpec Type %s" % self.type
        if self.type == AggregateManager.TYPE_OF:
            return egeni_api.update_rspec(self)
        else:
            return plc_api.update_rspec(self)
        
    def makeReservation(self):
        '''Request a reservation and return a message on success or failure'''
        
        if self.type == AggregateManager.TYPE_OF:
            error = egeni_api.reserve_slice(self)
        else:
            error = plc_api.reserve_slice(self)
            
        if error:
            # parse the error xml
            pass

class AggregateManagerForm(ModelForm):
    class Meta:
        model = AggregateManager
        fields = ('name', 'url', 'type')

class Node(models.Model):
    '''
    Anything that has interfaces. Can be a switch or a host or a stub.
    '''
    
    TYPE_OF = 'OF';
    TYPE_PL = 'PL';

    nodeId = models.CharField(max_length=200, primary_key=True)
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    
    is_remote = models.BooleanField()
    
    # @ivar remoteURL: indicates URL of controller
    remoteURL = models.URLField("Controller URL", verify_exists=False)
    
    # @ivar aggMgr: The AM that created the node or controls it
    aggMgr = models.ForeignKey(AggregateManager,
                               related_name='local_node_set',
                               blank=True,
                               null=True,
                               )
    
    # @ivar img_url: URL of the image used for when the node is drawn
    img_url = models.CharField(max_length=200)
    
    # initial x and y fields to use
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)

    # @ivar extra_context: Aggregate specific information
    extra_context = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "Node %s" % self.nodeId
    
    def get_absolute_url(self):
        return('node_detail', [str(self.aggMgr.id), str(self.nodeId)])
    get_absolute_url = permalink(get_absolute_url)

class Interface(models.Model):
    '''Describes a port and its connection'''
    portNum = models.PositiveSmallIntegerField(blank=True, null=True)
    ownerNode = models.ForeignKey(Node)
    remoteIfaces = models.ManyToManyField('self', symmetrical=False, through="Link")
    
    # PlanetLab additional things
    name = models.CharField(max_length=200, blank=True, null=True)
    addr = models.IPAddressField(blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)

    # @ivar extra_context: Aggregate specific information
    extra_context = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "Interface %u of node %s" % (self.portNum, self.ownerNode.nodeId)
        
class Link(models.Model):
    '''
    Stores information about the unidirectional connection between
    two nodes.
    '''
    
    src = models.ForeignKey(Interface, related_name='src_link_set')
    dst = models.ForeignKey(Interface, related_name='dst_link_set')
    
    # @ivar extra_context: Aggregate specific information
    extra_context = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "Link from " + self.src.__unicode__() \
                + " to " + self.dst.__unicode__()

class Slice(models.Model):
    '''This is created by a user (the owner) and contains
    multiple reservations from across different aggregate managers'''
    
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=200, unique=True)
    controller_url = models.CharField('OpenFlow Controller URL', max_length=200)
    nodes = models.ManyToManyField(Node, through="NodeSliceStatus")
    links = models.ManyToManyField(Link, through="LinkSliceStatus")
    committed = models.BooleanField()
    aggMgrs = models.ManyToManyField(AggregateManager, verbose_name="Aggregates")

    # nodes that this slice has seen. We use this to store a user's
    # x,y settings and other per-slice per-node settings
    gui_nodes = models.ManyToManyField(Node, through="NodeSliceGUI", related_name='gui_slice_set')
    
    def get_absolute_url(self):
        return('slice_flash_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)
    
    def has_interface(self, iface):
        '''
        return true if the interface is a src or dst in any link in
        this slice
        '''
        return (self.links.filter(src=iface).count()
                + self.links.filter(src=iface).count()) > 0
    
class NodeSliceStatus(models.Model):
    '''
    Tracks information about the node in the slice.
    '''
    
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)

    reserved = models.BooleanField()
    removed = models.BooleanField()
    has_error = models.BooleanField()
    
    # PlanetLab additional fields
    cpu_min = models.IntegerField(blank=True, null=True)
    cpu_share = models.IntegerField(blank=True, null=True)
    cpu_pct = models.IntegerField(blank=True, null=True)

class NodeSliceGUI(models.Model):
    '''
    Tracks information about the nodes in the GUI when
    shown for this slice.
    '''
    
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    
    x = models.FloatField()
    y = models.FloatField()

class LinkSliceStatus(models.Model):
    '''
    Tracks information about the link in the slice.
    '''
    
    slice = models.ForeignKey(Slice)
    link = models.ForeignKey(Link)
    
    reserved = models.BooleanField()
    removed = models.BooleanField()
    has_error = models.BooleanField()
    
class SliceForm(ModelForm):
    class Meta:
        model = Slice
        fields = ('name', 'controller_url', 'aggMgrs')

class FlowSpace(models.Model):
    TYPE_ALLOW = 1
    TYPE_DENY  = -1
    TYPE_RD_ONLY = 0
    
    POLICY_TYPE_CHOICES={TYPE_ALLOW: 'Allow',
                         TYPE_DENY: 'Deny',
                         TYPE_RD_ONLY: 'Read Only',
                         }

    policy = models.SmallIntegerField(choices=POLICY_TYPE_CHOICES.items())
    dl_src = models.CharField(max_length=17)
    dl_dst = models.CharField(max_length=17)
    dl_type = models.CharField(max_length=5)
    vlan_id = models.CharField(max_length=4)
    nw_src = models.CharField(max_length=18)
    nw_dst = models.CharField(max_length=18)
    nw_proto = models.CharField(max_length=3)
    tp_src = models.CharField(max_length=5)
    tp_dst = models.CharField(max_length=5)
    slice = models.ForeignKey(Slice, null=True, blank=True)
    
    def __unicode__(self):
        return("Policy: "+FlowSpace.POLICY_TYPE_CHOICES[self.policy]
               +", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)

class FlowSpaceForm(ModelForm):
    # TODO: add validation using policy manager
    class Meta:
        model=FlowSpace
        exclude = ('slice')

class DatedMessage(models.Model):
    TYPE_ERROR = 'error'
    TYPE_WARNING = 'warning'
    TYPE_ANNOUNCE = 'announcement'
    
    MSG_TYPE_CHOICES={TYPE_ERROR: 'Error',
                      TYPE_WARNING: 'Warning',
                      TYPE_ANNOUNCE: 'Announcement',
                     }
    type = models.CharField(max_length=20, choices=MSG_TYPE_CHOICES.items())
    datetime = models.DateTimeField(auto_now=True, auto_now_add=True)
    text = models.TextField()
    
    def format_date(self):
        return self.datetime.strftime("%Y-%m-%d")

    def format_time(self):
        return self.datetime.strftime("%H:%M:%S")
    
    def __unicode__(self):
        return "%s %s - %s" % (self.format_date(), self.format_time(), self.text)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name="created_user_set")
    is_aggregate_admin = models.BooleanField()
    is_user_admin = models.BooleanField()
    is_researcher = models.BooleanField()
    
    def __unicode__(self):
        return "User profile for user %s" % self.user.username
    
    @classmethod
    def get_or_create_profile(cls, user):
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            if user.is_staff or user.is_superuser:
                profile = cls.objects.create(
                                user=user,
                                is_aggregate_admin=True,
                                is_user_admin=True,
                                is_researcher=True,
                                )
            else:
                profile = cls.objects.create(
                                user=user,
                                is_aggregate_admin=False,
                                is_user_admin=False,
                                is_researcher=False,
                                )
        return profile
