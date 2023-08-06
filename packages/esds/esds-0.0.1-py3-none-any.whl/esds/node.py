import threading,importlib,queue
from esds.rcode import RCode

class Node:
    available_node_id=0
    def __init__(self,src,interfaces):
        """
        self.chest: contains mutex protected data
        """
        self.node_id=Node.available_node_id
        Node.available_node_id+=1 # Refresh node id
        self.src=src # Store the node source code
        self.args=None # Store the node arguments (passed through Simulator.create_node()
        self.rargs=None # Store the requests arguments
        self.plugins=list() # Contains all registered node plugins
        self.rqueue=queue.Queue() # Receive simulator acknowledgments
        self.chest={"state":"running", "turned_on":True, "request": None, "interfaces":dict(), "interfaces_queue_size":dict(), "pending_plugin_notify":0}
        for interface in interfaces:
            self.chest["interfaces"][interface]=queue.Queue()
            self.chest["interfaces_queue_size"][interface]=0
        self.chest_lock=threading.Lock() # To access/modify self.chest

    def plugin_register(self,plugin):
        self.plugins.append(plugin)

    def plugin_notify(self,reason,args=None,time=None):
        """
        This function strives to avoid using Python specific features
        """
        for p in self.plugins:
            if reason == "receive_return" or reason == "receivet_return":
                p.on_receive_return(args[0],args[1],args[2],args[3])
            if reason == "send_call":
                p.on_send_call(args[0],args[1],args[2],args[3])
            if reason == "send_return":
                p.on_send_return(args[0],args[1],args[2],args[3],args[4])
            if reason == "on_communication_end":
                p.on_communication_end(time,args)
            if reason == "turn_off_return":
                p.on_turn_off()
            if reason == "turn_on_return":
                p.on_turn_on()
            if reason == "terminated":
                p.on_terminated()

    def __getitem__(self,key):
        self.chest_lock.acquire()
        value=self.chest[key]
        self.chest_lock.release()
        return value

    def __setitem__(self,key,value):
        self.chest_lock.acquire()
        value=self.chest[key]=value
        self.chest_lock.release()

    def abort(self,reason):
        self.rargs=reason
        self["request"]="abort"
        self["state"]="call_non_blocking"
        while True: continue

    def log(self,msg):
        if type(msg) != str:
            self.abort("log() called with a non-string argument")
        self.rargs=msg
        self["request"]="log"
        self["state"]="call_non_blocking"
        self.wait_ack(["log"])

    def read(self, register):
        self["request"]="read"
        self.rargs=register
        self["state"]="call_non_blocking"
        ack=self.wait_ack(["read"])
        return ack[1]

    def wait(self,duration):
        if type(duration) != int and type(duration) != float:
            self.abort("wait() called with a non-number duration")
        elif duration < 0:
            self.abort("wait() called with a negative duration (duration="+str(duration)+")")
        elif duration == 0:
            return
        self.rargs=duration
        self["request"]="notify_add"
        self["state"]="call_non_blocking"
        self.wait_ack(["notify_add"])
        self["state"]="pending"
        self.wait_ack(["notify"])

    def wait_end(self):
        self["request"]="wait_end"
        self["state"]="call_blocking"
        self.wait_ack(["wait_end"])
        ack=self.wait_ack(["sim_end"])
        self.rqueue.put(ack) # To allow self.run() to catch the sim_end event

    def turn_off(self):
        self["turned_on"]=False
        self["request"]="turn_off"
        self["state"]="call_non_blocking"
        self.wait_ack(["turn_off"])
        self.plugin_notify("turn_off_return")
        
    def turn_on(self):
        self["turned_on"]=True
        self["request"]="turn_on"
        self["state"]="call_non_blocking"
        self.wait_ack(["turn_on"])
        self.plugin_notify("turn_on_return")
        
    def send(self, interface, data, datasize, dst, receiver_required=False):
        if interface not in self["interfaces"]:
            self.abort("send() called with an unknown interface \""+interface+"\"")
        elif type(datasize) != int and type(datasize) != float:
            self.abort("send() called with a non-number datasize")
        elif type(dst) != int and type(dst) != float and dst != None:
            self.abort("send() called with a non-number dst (wired interfaces) or dst is not None (wireless interfaces)")
        elif not self["turned_on"]:
            self.abort("send() called while node is turned off")
        self.plugin_notify("send_call",(interface,data,datasize,dst))
        self.rargs=(interface, data, datasize, dst,receiver_required)
        self["request"]="send"
        self["state"]="call_blocking"
        ack=self.wait_ack(["send","send_cancel"])
        self.plugin_notify("send_return",(interface,data,datasize,dst,ack[1]))
        return ack[1]

    def sendt(self, interface, data, datasize, dst, timeout, receiver_required=False):
        if interface not in self["interfaces"]:
            self.abort("sendt() called with an unknown interface \""+interface+"\"")
        elif type(datasize) != int and type(datasize) != float:
            self.abort("sendt() called with a non-number datasize")
        elif type(timeout) != int and type(timeout) != float:
            self.abort("sendt() called with a non-number timeout")
        elif timeout < 0:
            self.abort("sendt() called with a negative timeout (timeout="+str(timeout)+")")
        elif type(dst) != int and type(dst) != float and dst != None:
            self.abort("send() called with a non-number dst (wired interfaces) or dst is not None (wireless interfaces)")
        elif not self["turned_on"]:
            self.abort("sendt() called while node is turned off")
        self.rargs=timeout
        self["request"]="timeout_add"
        self["state"]="call_non_blocking"
        self.wait_ack(["timeout_add"])
        self.rargs=(interface, data, datasize, dst,receiver_required)
        self["request"]="send"
        self["state"]="call_blocking"
        ack=self.wait_ack(["send","timeout","send_cancel"])
        status=RCode.TIMEOUT_EXPIRE
        if ack[0] == "timeout":
            self["request"]="send_cancel"
            self["state"]="call_non_blocking"
            self.wait_ack(["send_cancel"])
        else:
            self["request"]="timeout_remove"
            self["state"]="call_non_blocking"
            self.wait_ack(["timeout_remove"])
            status=ack[1]
        return status
        
    def receive(self,interface):
        if interface not in self["interfaces"]:
            self.abort("receive() called with an unknown interface \""+interface+"\"")
        elif not self["turned_on"]:
            self.abort("receive() called while node is turned off")
        self["request"]="receive"
        self.rargs=interface
        self["state"]="call_blocking"
        self.wait_ack(["receive"])
        data,start_at,end_at=self["interfaces"][interface].get()
        self.plugin_notify("receive_return",(interface,data,start_at,end_at))
        return (RCode.SUCCESS,data)

    def receivet(self,interface, timeout):
        if interface not in self["interfaces"]:
            self.abort("receivet() called with an unknown interface \""+interface+"\"")
        elif type(timeout) != int and type(timeout) != float:
            self.abort("receivet() called with a non-number timeout")
        elif timeout < 0:
            self.abort("receivet() called with a negative timeout (timeout="+str(timeout)+")")
        elif not self["turned_on"]:
            self.abort("receivet() called while node is turned off")
        self.rargs=timeout
        self["request"]="timeout_add"
        self["state"]="call_non_blocking"
        self.wait_ack(["timeout_add"])
        self["request"]="receive"
        self.rargs=interface
        self["state"]="call_blocking"
        ack=self.wait_ack(["receive","timeout"])
        result=(RCode.TIMEOUT_EXPIRE,None)
        if ack[0] != "timeout":
            self["request"]="timeout_remove"
            self["state"]="call_non_blocking"
            self.wait_ack(["timeout_remove"])
            data,start_at,end_at=self["interfaces"][interface].get()
            self.plugin_notify("receivet_return",(interface,data,start_at,end_at))
            result=(RCode.SUCCESS,data)
        return result

    def wait_ack(self, ack_types):
        """
        Wait for specific acks from the request queue (rqueue)
        """
        ack_buffer=list() # To filter ack
        ack=None
        while True:
            ack=self.rqueue.get() # Wait for simulator acknowledgments
            if ack[0] == "plugin_notify":
                self.plugin_notify(ack[1],ack[3],time=ack[2])
                self["pending_plugin_notify"]-=1
            elif ack[0] not in ack_types:
                ack_buffer.append(ack)
            else:
                break
        # Push back the filtered ack
        for cur_ack in ack_buffer:
            self.rqueue.put(cur_ack)
        return(ack)
    
    def sync(self):
        """
        Wait until node stop running
        """
        while self["state"] == "running" or self["pending_plugin_notify"] > 0:
            pass
        
    def run(self,args):
        """
        Load and run the user program
        """
        self.node=importlib.import_module(self.src)
        self.args=args # Allow access to arguments
        self.node.execute(self)
        self["state"]="terminated"
        self.wait_ack(["sim_end"])
