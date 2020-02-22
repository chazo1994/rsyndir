from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.choosereactor import install_reactor
import os, sys, logging
import time

from syncdir import utils, tree
reactor = install_reactor()

class SourceSyncProtocol(WebSocketClientProtocol):
    def __init__(self, root_node):
        self.root_node = root_node
        self.is_busy = False
        self.isSending = False
        self.END_KEY = "end"
        self.index = 0
        WebSocketClientProtocol.__init__(self)

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def sendHello(self):
        self.sendMessage("Hello, world!".encode('utf8'))
        self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
    def sendfiles(self):
        current_node = root_node
        while True:
            for children in current_node.childrens:

                if children.state != 0:
                    if os.path.isdir(children.path):
                        ##send dir
                        pass
                    else:
                        ##send file
                        pass



    def onMessage(self, payload, isBinary):

        if not isBinary:
            pass
        else:
            pass

    #@synchronized_with_attr("lock")
    def sendMessage(self, payload, isBinary=False, fragmentSize=None):
        #super(MerlinClientProtocol,self).sendMessage(payload, isBinary, fragmentSize=fragmentSize)
        if not isBinary:
            super(SourceSyncProtocol, self).sendMessage(payload, isBinary)
        elif fragmentSize == None:
            super(SourceSyncProtocol, self).sendMessage(payload, isBinary)
        else:
            if fragmentSize < 1:
                raise Exception("payload fragment size must be at least 1 (was %d)" % fragmentSize)
            n = len(payload)
            i = 0
            while True:
                j = i + fragmentSize
                if j >= n:
                    super(SourceSyncProtocol, self).sendMessage(payload[i:n], isBinary)
                    break
                else:
                    super(SourceSyncProtocol, self).sendMessage(payload[i:j], isBinary)
                i = j

    def safeSendMessage(self, payload, isBinary=False, fragmentSize=None):
        reactor.callFromThread(self.sendMessage,payload,isBinary,fragmentSize)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        if self.is_busy:
            if hasattr(self,"communicator"):
                self.communicator.signal.stop_signal = True
    def release_process(self):
        self.is_busy = False

class SourceSyncClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    """
    Example WebSocket client factory. This creates a new instance of our protocol
    when the client connects to the server.
    """

    def buildProtocol(self, addr):
        proto = SourceSyncProtocol(self.root_node)
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)

if __name__ == '__main__':

    import argparse

    from twisted.python import log
    from twisted.internet.endpoints import clientFromString

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("--rootdir", default=".")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("--websocket", default="unix:/tmp/mywebsocket",
                        help='WebSocket client Twisted endpoint descriptor, e.g. "tcp:172.1.16.33:9000" or "unix:/tmp/mywebsocket".')

    parser.add_argument("--wsurl", default=u"ws://127.0.0.1:9000",
                        help='WebSocket URL (must suit the endpoint), e.g. ws://127.0.0.1:9000.')

    args = parser.parse_args()

    # start Twisted logging to stdout
    #log.startLogging(sys.stdout)
    log.startLogging(sys.stdout)
    logger = logging.getLogger("main")
    logger.info("hihi")
    logger.debug("hihi")
    # we use an Autobahn utility to import the "best" available Twisted reactor
    # from autobahn.twisted.choosereactor import install_reactor

    # reactor = install_reactor()
    print("Running on reactor {}".format(reactor))
    print("link: %s" % args.websocket)
    # start a WebSocket client
    wsfactory = SourceSyncClientFactory(args.wsurl)
    root_node = utils.build_dir_tree(args.rootdir)
    wsfactory.root_node = root_node
    websocket_params = args.websocket.split(":")
    while True:
        time.sleep(0.01)
        total_change = utils.update_status(root_node)
        if total_change == 0:
            continue
        root_node.total_change = total_change
        if websocket_params[0] == "unix":
            reactor.connectUNIX(websocket_params[1], wsfactory)
        elif websocket_params[0] == "tcp":
            port = 8081
            try:
                port = int(websocket_params[2])
            except:
                print("TCP port parse error")
                sys.exit(1)
            reactor.connectTCP(websocket_params[1], port, wsfactory)
        else:
            print("This protocol not be supported yet!")
            sys.exit(2)
    # wsclient = clientFromString(reactor, args.websocket)
    # wsclient.connect(wsfactory)

    #reactor.connectTCP("127.0.0.1", 8081, wsfactory)
    #reactor.connectUNIX("/tmp/mywebsocket",wsfactory)
    reactor.run()

    # now enter the Twisted reactor loop
    #reactor.run()
