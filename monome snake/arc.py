import socket, select, pybonjour, threading, random, monome
from OSC import OSCClient, OSCServer, OSCMessage, NoCallbackError

class Arc(OSCServer):
    def __init__(self, address):
        OSCServer.__init__(self, ('', 0))
        self.client.connect(address)
        host, port = self.client.socket.getsockname()
        
        self.focused = False
        #self.server_host = host
        #self.server_port = port
        self.prefix = monome.DEFAULT_PREFIX
        
        self.addMsgHandler('default', self.monome_handler)
        self.addMsgHandler('/sys/connect', self.sys_misc)
        self.addMsgHandler('/sys/disconnect', self.sys_misc)
        self.addMsgHandler('/sys/id', self.sys_misc)
        self.addMsgHandler('/sys/size', self.sys_size)
        self.addMsgHandler('/sys/host', self.sys_host)
        self.addMsgHandler('/sys/port', self.sys_port)
        self.addMsgHandler('/sys/prefix', self.sys_prefix)
        self.addMsgHandler('/sys/rotation', self.sys_misc)
        
        # handshake
        msg = OSCMessage("/sys/host")
        msg.append(host)
        self.client.send(msg)
        
        msg = OSCMessage("/sys/port")
        msg.append(port)
        self.client.send(msg)
        
        msg = OSCMessage("/sys/info")
        self.client.send(msg)
        
        #self.app_callback = None
    
    def sys_misc(self, *args):
        pass
    
    def sys_host(self, addr, tags, data, client_address):
        pass
    
    def sys_port(self, addr, tags, data, client_address):
        host, port = self.server_address
        if port == data[0]:
            self.focused = True
            self.send('/sys/prefix', self.prefix)
        else:
            self.focused = False
            print "lost focus (device changed port)"
    
    # prefix confirmation
    def sys_prefix(self, addr, tags, data, client_address):
        self.prefix = monome.fix_prefix(data[0])
    
    def sys_size(self, addr, tags, data, client_address):
        pass
    
    def send(self, path, *args):
        msg = OSCMessage(path)
        map(msg.append, args)
        self.client.send(msg)
    
    def led_all(self, n, l):
        self.send("%s%s" % (self.prefix, "/ring/all"), n, l)
    
    def led_set(self, n, x, l):
        self.send("%s%s" % (self.prefix, "/ring/set"), n, x, l)
    
    def led_range(self, n, x1, x2, l):
        self.send("%s%s" % (self.prefix, "/ring/range"), n, x1, x2, l)
    
    def monome_handler(self, addr, tags, data, client_address):
        if addr.startswith(self.prefix):
            try:
                method = addr.replace(self.prefix, "", 1).replace("/", "_").strip("_")
                getattr(self, method)(*data)
            except AttributeError:
                pass
        else:
			raise NoCallbackError(addr)
    
    # threading
    def poll(self):
        ready = select.select([self], [], [])[0]
        for r in ready:
            self.handle_request()
    
    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
    
    def run(self):
        self.running = True
        while self.running:
            self.poll()
        self.close()
    
    def close(self):
    	self.running = False
    	self.led_all(0, 0)
    	self.led_all(1, 0)
