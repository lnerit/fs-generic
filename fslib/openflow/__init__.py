# version 1 OpenflowSwitch and OpenflowController
# from ofmessage_v1 import * 
# from ofnode_v1 import *

# version 2: direct integration and monkeypatching of POX

## Change zone ##
# version 3: this file is deprecated and monkeypatching is not used anymore

from fslib.common import fscore, get_logger
from fslib.node import Node
from importlib import import_module

import pox
import pox.core

if 'initialize' in dir(pox.core):
    pox.core.initialize()

from pox.openflow import libopenflow_01 as oflib
import pox.openflow as openflow_component
import pox.openflow.of_01 as ofcore
import pox.openflow.of_01 as ofcore_gen

class RuntimeError(Exception):
    pass

class FakePoxTimer(object):
    '''Timer class that supports same interface as pox.lib.recoco.Timer'''

    timerid = 0
    def __init__ (self, timeToWake, callback, absoluteTime = False,
                recurring = False, args = (), kw = {}, scheduler = None,
                started = True, selfStoppable = True):

        if absoluteTime and recurring:
            raise RuntimeError("Can't have a recurring timer for an absolute time!")

        if absoluteTime:
            raise RuntimeError("Can't have an absolute time in FakePoxTimer")

        self._self_stoppable = selfStoppable
        self._timeToWake = timeToWake

        self.id = "poxtimer{}".format(FakePoxTimer.timerid)
        FakePoxTimer.timerid += 1

        self._recurring = recurring
        self._callback = callback
        self._args = args
        self._kw = kw
        get_logger().debug("Setting fake pox timer callback {} {}".format(self._timeToWake, self._callback))
        fscore().after(self._timeToWake, self.id, self.docallback, None)

    def cancel(self):
        get_logger().debug("Attempting to cancel fake POX timer {}".format(self.id))
        fscore().cancel(self.id)

    def docallback(self, *args):
        get_logger().debug("In fake pox timer callback {} {}".format(self._timeToWake, self._callback))
        rv = self._callback(*self._args, **self._kw)
        if rv and self._recurring:
            fscore().after(self._timeToWake, self.id, self.docallback, None)
        

class PoxLibPlug(object):
    def __getattr__(self, attr):
        print "Pox library plug get attribute {}".format(attr)
        assert(False),"Unexpected POX call: monkeypatch may need update."

'''
## Change zone
Change this connection to remote controller
'''

# print "bla1"
# origConn = ofcore.Connection
origConn_gen = ofcore_gen.Connection
# print "bla2"

class GenOpenflowConnection(ofcore_gen.Connection):
    def __init__(self, sock, controller_send, switchname="wrong", dpid=None):
        self.sendfn = controller_send
        self.idle_time = None
        self.connect_time = None
        self.switchname = switchname
        self.sock = -1
        print "Connection init"
        origConn_gen.__init__(self, -1)
        print "After connection init"
        self.ofnexus = pox.core.core.OpenFlowConnectionArbiter.getNexus(self)
        self.dpid = dpid
        self.ofnexus.connections[dpid] = self
                
    def send(self, ofmessage):
        get_logger().info("Doing callback in OF connection from controller->switch {}".format(ofmessage)) 
        print "unknown", self.switchname
        self.sendfn(self.switchname, ofmessage)

    def read(self):
        print "Got read() in Fake Connection, but we expect simrecv to be called"

    def simrecv(self, msg):
        # print "Received message in FakeOpenflowConnection:", str(msg)
        print "seq 3"
        if msg.version != oflib.OFP_VERSION:
            get_logger().debug("Bad OpenFlow version (0x%02x) on connection %s"
                % (ord(self.buf[offset]), self))
            return False # Throw connection away

        # don't need to pack/unpack because we control message send/recv
        # new_offset,msg = unpackers[ofp_type](self.buf, offset)
        ofp_type = msg.header_type

        try:
            from pox.openflow.of_01 import handlers
            h = handlers[ofp_type]
            h(self, msg)
        except:
            get_logger().debug("%s: Exception while handling OpenFlow message:\n" +
                      "%s %s", self,self,
                      ("\n" + str(self) + " ").join(str(msg).split('\n')))
        return True

    def fileno(self):
        return -1

    def close(self):
        pass

'''
Original function written by Joel

class FakeOpenflowConnection(ofcore.Connection):
    def __init__(self, sock, controller_send, switchname="wrong", dpid=None):
        self.sendfn = controller_send
        self.idle_time = None
        self.connect_time = None
        self.switchname = switchname
        self.sock = -1
        print "Connection init"
        origConn.__init__(self, -1) 
        origConn.__init__(self, -1)
        print "After connection init"
        self.ofnexus = pox.core.core.OpenFlowConnectionArbiter.getNexus(self)
        self.dpid = dpid
        self.ofnexus.connections[dpid] = self
                
    def send(self, ofmessage):
        get_logger().debug("Doing callback in OF connection from controller->switch {}".format(ofmessage)) 
        print "unknown", self.switchname
        self.sendfn(self.switchname, ofmessage)

    def read(self):
        print "Got read() in Fake Connection, but we expect simrecv to be called"

    def simrecv(self, msg):
        # print "Received message in FakeOpenflowConnection:", str(msg)
        print "seq 3"
        if msg.version != oflib.OFP_VERSION:
            get_logger().debug("Bad OpenFlow version (0x%02x) on connection %s"
                % (ord(self.buf[offset]), self))
            return False # Throw connection away

        # don't need to pack/unpack because we control message send/recv
        # new_offset,msg = unpackers[ofp_type](self.buf, offset)
        ofp_type = msg.header_type

        try:
            from pox.openflow.of_01 import handlers
            h = handlers[ofp_type]
            h(self, msg)
        except:
            get_logger().debug("%s: Exception while handling OpenFlow message:\n" +
                      "%s %s", self,self,
                      ("\n" + str(self) + " ").join(str(msg).split('\n')))
        return True

    def fileno(self):
        return -1

    def close(self):
        pass
'''

def get_pox_logger(*args, **kwargs):
    return get_logger()

def monkey_patch_pox():
    '''Override two key bits of POX functionality: the Timer class and
    the openflow connection class.  Other overrides are mainly to ensure
    that nothing unexpected happens, but are strictly not necessary at
    present (using betta branch of POX)'''
    # get_logger().info("Monkeypatching POX for integration with fs")
    get_logger().info("Controller integration with fs")

    fakerlib = PoxLibPlug()
    import pox.lib.recoco as recoco
    setattr(recoco, "Timer", FakePoxTimer)

    import pox.lib
    setattr(pox.lib, "ioworker", fakerlib)
    setattr(pox.lib, "pxpcap", fakerlib)
    setattr(pox.lib, "socketcapture", fakerlib)

    import pox
    setattr(pox, "messenger", fakerlib)
    setattr(pox, "misc", fakerlib)

    # setattr(ofcore, "Connection", FakeOpenflowConnection)
    # setattr(ofcore, "OpenFlow_01_Task", fakerlib)

    setattr(ofcore_gen, "Connection", GenOpenflowConnection)
    setattr(ofcore_gen, "OpenFlow_01_Task", fakerlib)

    import pox.core 
    setattr(pox.core, "getLogger", get_pox_logger)


def load_pox_component(name):
    '''Load a pox component by trying to import the named module and
       invoking launch().  Raise a runtime error if something goes wrong.'''

    # print "MP happens here? 3"
    log = get_logger()
    try:
        m = import_module(name)
        if 'launch' not in dir(m):
            log.error("Can't load POX module {}".format(name))
            raise RuntimeError('No launch function in module {}'.format(name))
        else:
            log.debug("Loading POX component {}".format(name))
            # FIXME: component launch needs some rework.
            # import pox.boot
            # pox.boot._do_launch([name])

            if m.launch.func_code.co_argcount == 0:
                m.launch()
            elif m.launch.func_code.co_argcount >= 1:
                m.launch(m.__dict__)

            log.debug("Loaded POX component {}".format(name))

    except ImportError,e:
        log.error("Error trying to import {} POX component".format(name))
        raise RuntimeError(str(e))

monkey_patch_pox()
load_pox_component("pox.openflow")
# get_logger().info("Kicking POX Up")
# pox.core.core.goUp()
get_logger().debug("POX components: {}".format(pox.core.core.components))
# print "MP - 5"
from pox_bridge import *
# print "MP - 6"
