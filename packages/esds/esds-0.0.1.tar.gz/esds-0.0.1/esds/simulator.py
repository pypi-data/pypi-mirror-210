import numpy as np
import threading,sys,time
from esds.node import Node
from esds.rcode import RCode
from esds.debug import Debug

class Simulator:
    """
    Flow-Level Discrete Event Simulator for Cyber-Physical Systems
    The general format for an event is (type,timestamp,event,priority)
    Event types:
        - 0 send                  (0,timestamp,(src,dst,interface,data,datasize,duration,datasize_remaining,start_timestamp, perform_delivery, receiver_required), 2)
        - 1 timeout               (1,timestamp,node_id,3)
        - 2 breakpoint_manual     (2,timestamp,0,1)
        - 3 breakpoint_auto       (3,timestamp,0,1)
        - 4 notify                (4,timestamp,node_id,0)


    Very important notes: 
    - When the simulator wakes up a node (changing is state to running) data that should be received by that node 
    on the current simulated time SHOULD be in the queue! Thus, the send event must be handle before the other event (priority equals to 1). 
    Otherwise plugings such as the power states one may not gives accurate results because of missing entries in the nodes received queues.
    - The state of a node should always be updated (e.g node["state"]="running") BEFORE updating its 
    queue (e.g node.rqueue.put(("timeout_remove",0))
    - Notify as the same behavior as timeout. Except it has the highest priority among all the events! This is particularly usefull for wait events which SHOULD
    be handle before any other one. That way after a wait, nodes a ready perform receivet() with timeout=0.
    """
    
    def __init__(self,netmat):
        """
        Format of netmat: { "interface": {"bandwidth": numpy_matrix_2D, "latency": numpy_matrix_2D, "is_wired":bool}}
        For wireless interfaces the diagonals of the bandwidth and latency matrices are very important.
        They determine the duration of the tranmission for THE SENDER. It allows to have a different tx duration per node and per interface.
        Thus, at each wireless communication, an addionnal event is created for the sender that corresponds to a send to himself (diagonals of the matrices) used
        to unlock him from the api.send() call. Consequently, the duration of the transmission (by the sender) can be 
        different from the time at which the receivers actually receive the data (non-diagonal entries of the matrices).
        """
        self.netmat=netmat
        self.nodes=list()
        self.sharing=dict()
        for interface in netmat.keys():
            if netmat[interface]["is_wired"]:
                self.sharing[interface]=np.zeros(len(netmat[interface]["bandwidth"]))
        self.events=np.empty((0,4),dtype=object)
        self.events_dirty=True # For optimization reasons
        self.startat=-1
        self.time=0
        self.debug_file_path="./esds.debug"
        self.precision=".3f"
        self.interferences=True
        self.wait_end_nodes=list() # Keep track of nodes that wait for the end of the simulation
        self.time_truncated=format(self.time,self.precision) # Truncated version is used in log print
        self.debug=None # No debug by default

    def update_network(self,netmat):
        for event in self.events:
            if int(event[0]) == 0:
                cur_event=event[2]
                ts=float(event[1])
                src_id,dst_id,interface, data, datasize,duration, datasize_remaining,start_at,perform_delivery,receiver_required=cur_event
                new_bw=netmat[interface]["bandwidth"][int(src_id),int(dst_id)]
                old_bw=self.netmat[interface]["bandwidth"][int(src_id),int(dst_id)]
                new_lat=netmat[interface]["latency"][int(src_id),int(dst_id)]
                old_lat=self.netmat[interface]["latency"][int(src_id),int(dst_id)]
                if new_bw != old_bw or new_lat != old_lat:
                    new_datasize_remaining=float(datasize_remaining)*((ts-self.time)/float(duration))
                    if new_datasize_remaining > 0:
                        latency_factor=new_datasize_remaining/float(datasize)
                        if self.netmat[interface]["is_wired"]:
                            new_duration=new_datasize_remaining*8/(new_bw/self.sharing[interface][int(dst_id)])+new_lat*latency_factor
                        else:
                            new_duration=new_datasize_remaining*8/new_bw+new_lat*latency_factor
                        event[1]=self.time+new_duration
                        event[2][6]=new_datasize_remaining
                        event[2][5]=new_duration
        self.netmat=netmat
          
    def create_node(self, src, args=None):
        """
        Create a node thread and run it
        """
        node=Node(src, self.netmat.keys())
        self.nodes.append(node)
        thread=threading.Thread(target=node.run,args=[args]) # There must be "daemon=True" as a parameter, but we removed it to be compatible with older version of python
        thread.start()

    def log(self,msg,node=None):
        src = "esds" if node is None else "n"+str(node)
        logline="[t="+str(self.time_truncated)+",src="+src+"] "+msg
        if self.debug is not None:
            self.debug.append_log(logline)
        print(logline)

    def sort_events(self):
        """
        Sort the events by timestamp and priorities
        """
        sorted_indexes=np.lexsort((self.events[:,3],self.events[:,1]))
        self.events=self.events[sorted_indexes]
    
    def sync_node_non_blocking(self,node, timeout_remove_only=False):
        """
        Process all call request and wait for Node.sync() to return
        """
        node.sync()
        while node["state"] == "call_non_blocking":
            if node["request"] == "timeout_remove":
                selector=list()
                for event in self.events:
                    if event[0] == 1 and event[2]==node.node_id:
                        selector.append(True)
                    else:
                        selector.append(False)
                self.events=self.events[~np.array(selector)]
                node["state"]="running"
                node.rqueue.put(("timeout_remove",RCode.SUCCESS))
            elif timeout_remove_only:
                break
            elif not timeout_remove_only:
                if node["request"] == "log":
                    self.log(node.rargs,node=node.node_id)
                    node["state"]="running"
                    node.rqueue.put(("log",RCode.SUCCESS))
                elif node["request"] == "timeout_add":
                    self.add_event(1,self.time+node.rargs,node.node_id,priority=3)
                    node["state"]="running"
                    node.rqueue.put(("timeout_add",RCode.SUCCESS))
                elif node["request"] == "notify_add":
                    self.add_event(4,self.time+node.rargs,node.node_id,priority=0)
                    node["state"]="running"
                    node.rqueue.put(("notify_add",RCode.SUCCESS))
                elif node["request"] == "notify_remove":
                    selector=list()
                    for event in self.events:
                        if event[0] == 4 and event[2]==node.node_id:
                            selector.append(True)
                        else:
                            selector.append(False)
                    self.events=self.events[~np.array(selector)]
                    node["state"]="running"
                    node.rqueue.put(("notify_remove",RCode.SUCCESS))
                elif node["request"] == "abort":
                    self.log("Simulation aborted: "+node.rargs,node=node.node_id)
                    exit(1)
                elif node["request"] == "read":
                    node["state"]="running"
                    if node.rargs == "clock":
                        node.rqueue.put(("read",float(self.time)))
                    elif node.rargs[0:5] == "ncom_": # ncom_<interface> register
                        interface=node.rargs[5:]
                        count=0
                        # Count number of communication on interface
                        for event in self.events:
                            if event[0] == 0 and event[2][1] == node.node_id and event[2][2] == interface:
                                count+=1
                        node.rqueue.put(("read",count))
                    else:
                        node.rqueue.put(("read",0)) # Always return 0 if register is unknown
                elif node["request"] == "turn_on":
                    node["state"]="running"
                    node.rqueue.put(("turn_on",RCode.SUCCESS))
                    self.log("Turned on",node=node.node_id)
                elif node["request"] == "turn_off":
                    # Update node state after turning off
                    node["state"]="running"
                    node.rqueue.put(("turn_off",RCode.SUCCESS))
                    self.log("Turned off",node=node.node_id)
                    # We cancel communication after node has turned off
                    self.cancel_communications(node.node_id,reason=RCode.RECEIVER_TURNED_OFF)
                elif node["request"] == "send_cancel":
                    self.cancel_communications(node.node_id)
                    node["state"]="running"
                    node.rqueue.put(("send_cancel",RCode.SUCCESS))
            node.sync()

    def cancel_communications(self, node_id, reason=RCode.UNKNOWN):
        if(len(self.events) == 0):
            return
        # Build list of impacted events
        selector=list()
        for event in self.events:
            if event[0]==0:
                src_id,dst_id,interface, data, datasize,duration,datasize_remaining,start_at,perform_delivery,receiver_required=event[2]
                is_wired=self.netmat[interface]["is_wired"]
                is_wireless=not is_wired
                if src_id == node_id:
                    selector.append(True)
                elif dst_id == node_id:
                    if is_wireless:
                        selector.append(True)
                    else:
                        if receiver_required:
                            selector.append(True)
                        else:
                            selector.append(False)
                            event[2][8]=False # So set delivery to False!!
                else:
                    selector.append(False)      
            else:
                selector.append(False)
        # Update sharing of wired communications and build sender to notify set
        senders_to_notify=set()
        for event in self.events[selector]:
            src_id,dst_id,interface, data, datasize,duration,datasize_remaining,start_at,perform_delivery,receiver_required=event[2]
            if self.netmat[interface]["is_wired"]:
                # If node is sender
                if src_id == node_id:
                    self.update_sharing(dst_id,-1,interface)
                else:
                    self.update_sharing(node_id,-1,interface)
                    senders_to_notify.add(src_id) # We do not notify sender here since it may change the event list (invalidate selector)
        # Notify plugins
        for event in self.events[selector]:
            src_id,dst_id,interface, data, datasize,duration,datasize_remaining,start_at,perform_delivery,receiver_required=event[2]
            if self.netmat[interface]["is_wired"]:
                self.notify_node_plugins(self.nodes[src_id], "on_communication_end", event)
                self.notify_node_plugins(self.nodes[dst_id], "on_communication_end", event)
            elif src_id == dst_id:
                self.notify_node_plugins(self.nodes[src_id], "on_communication_end", event)
            else:
                self.notify_node_plugins(self.nodes[dst_id], "on_communication_end", event)
        # Delete related events
        self.events=self.events[~(np.array(selector))]
        # Notify sender at the end to not corrupt the event list and invalidate selector
        for sender in senders_to_notify:
            # Notify sender (node that wired sharing is updated in the send_cancel request)
            sender_node=self.nodes[sender]
            sender_node["state"]="running"
            sender_node.rqueue.put(("send_cancel",reason))
            # The node should resume at current self.time. So, sync the sender now:
            self.sync_node_non_blocking(sender_node)
            self.sync_node_blocking(sender_node)


    def update_sharing(self, dst, amount,interface):
        """
        Manage bandwidth sharing on wired interfaces
        THIS FUNCTION SORT EVENTS SO BE CAREFUL SINCE IT CAN INVALIDATE SELECTORS
        """
        sharing=self.sharing[interface][dst]
        new_sharing=sharing+amount
        for event in self.events:
            if event[0] == 0 and self.netmat[event[2][2]]["is_wired"] and int(event[2][1]) == dst:
                remaining=event[1]-self.time
                if remaining > 0:
                    remaining=remaining/sharing if sharing>1 else remaining # First restore sharing
                    remaining=remaining*new_sharing if new_sharing > 1 else remaining # Then apply new sharing
                    event[2][5]=remaining # Update duration
                    event[1]=self.time+remaining # Update timestamp
        self.sharing[interface][dst]=new_sharing
        self.sort_events()

    def handle_interferences(self,sender,receiver, interface):
        """
        Interferences are detected by looking for conflicts between
        new events and existing events.
        """
        status=False
        selector=list()
        notify=set()
        for event in self.events:
            event_type=event[0]
            com=event[2]
            if event_type==0 and com[2] == interface:
                com_sender=int(com[0])
                com_receiver=int(com[1])
                select=False
                if receiver==com_sender:
                    status=True
                    notify.add(receiver)
                elif receiver==com_receiver:
                    status=True
                    select=True
                    notify.add(receiver)
                if sender==com_receiver and com_sender != com_receiver:
                    select=True
                    notify.add(sender)
                selector.append(select)
            else:
                selector.append(False)
        if len(selector) != 0:
            self.events=self.events[~np.array(selector)]
            for node in notify:
                self.log("Interferences on "+interface,node=node)
        return status
    
    def sync_node_blocking(self, node):
        """
        Collect events from the nodes
        """
        if node["state"] == "call_blocking":
            if node["request"] == "send":
                node["state"]="pending"
                interface, data, datasize, dst, receiver_required=node.rargs
                if dst != None: 
                    if not (dst >=0 and dst <=len(self.nodes)):
                        self.log("Invalid dst used in send() or sendt(), node "+str(dst)+" not found", node=node.node_id)
                        exit(1)
                if not self.communicate(interface, node.node_id, dst, data, datasize,receiver_required):
                    node["state"]="running"
                    node.rqueue.put(("send",RCode.RECEIVER_UNAVAILABLE))
                    # Do not forget to collect the next event (since current event did not happend)
                    # Be careful in node implementation to have no infinite loop when receiver_required=True
                    self.sync_node_non_blocking(node)
                    self.sync_node_blocking(node)
            elif node["request"] == "receive":
                interface=node.rargs
                if node["interfaces_queue_size"][interface] > 0:
                    node["interfaces_queue_size"][interface]-=1
                    node["state"]="running"
                    node.rqueue.put(("receive",RCode.SUCCESS))
                    # Do not forget to collect the next event. This is the only request which is processed here
                    self.sync_node_non_blocking(node)
                    self.sync_node_blocking(node)
            elif node["request"] == "wait_end":
                node["state"]="pending"
                node.rqueue.put(("wait_end",RCode.SUCCESS))
                self.wait_end_nodes.append(node.node_id)

    def communicate(self, interface, src, dst, data, datasize,receiver_required):
        """
        Create communication event between src and dst
        """
        nsrc=self.nodes[src]
        if self.netmat[interface]["is_wired"]:
            self.log("Send "+str(datasize)+" bytes to n"+str(dst)+" on "+interface,node=src)
            if not self.nodes[dst]["turned_on"] and receiver_required:
                return(False)
            self.update_sharing(dst,1,interface) # Update sharing first
            # Note that in the following we send more data than expected to handle bandwidth sharing (datasize*8*sharing):
            duration=datasize*8/(self.netmat[interface]["bandwidth"][src,dst]/self.sharing[interface][dst])+self.netmat[interface]["latency"][src,dst]
            self.add_event(0,duration+self.time,(src,dst,interface,data,datasize,duration,datasize,self.time,self.nodes[dst]["turned_on"],receiver_required))
        else:
            self.log("Send "+str(datasize)+" bytes on "+interface,node=src)
            for dst in self.list_receivers(nsrc,interface):
                if self.nodes[dst]["turned_on"]:
                    duration=datasize*8/self.netmat[interface]["bandwidth"][src,dst]+self.netmat[interface]["latency"][src,dst]
                    if src == dst:
                        # This event (where src == dst) is used to notify the sender when data is received!
                        # Correspond to the diagonal of the network matrices (bandwidth and latency)
                        self.add_event(0,duration+self.time,(src,dst,interface,data,datasize,duration,datasize,self.time,True,False))
                    elif not self.interferences:
                        self.add_event(0,duration+self.time,(src,dst,interface,data,datasize,duration,datasize,self.time,True,False))
                    elif not self.handle_interferences(src,dst, interface):
                        self.add_event(0,duration+self.time,(src,dst,interface,data,datasize,duration,datasize,self.time,True,False))
        return(True)
    def list_receivers(self,node,interface):
        """
        Deduce reachable receivers from the bandwidth matrix
        """
        selector = self.netmat[interface]["bandwidth"][node.node_id,] > 0
        return np.arange(0,selector.shape[0])[selector]

    def notify_node_plugins(self,node,callback,args):
        node["pending_plugin_notify"]+=1
        node.rqueue.put(("plugin_notify",callback,self.time,args))

    def add_event(self,event_type,event_ts,event,priority=2):
        """
        Call this function with sort=True the least amount of time possible
        """
        self.events=np.concatenate([self.events,[np.array([event_type,event_ts,np.array(event,dtype=object),priority],dtype=object)]]) # Add new events
        self.sort_events()
            
    def run(self, breakpoints=[],breakpoint_callback=lambda s:None,breakpoints_every=None,debug=False,interferences=True,debug_file_path="./esds.debug"):
        """
        Run the simulation with the created nodes
        """
        ##### Setup simulation
        self.startat=time.time()
        self.interferences=interferences
        self.debug_file_path=debug_file_path
        for bp in breakpoints:
            self.add_event(2,bp,0,1)
        if breakpoints_every != None:
            self.add_event(3,breakpoints_every,0,1)
        if debug:
            self.debug=Debug(self,self.debug_file_path, breakpoints,breakpoints_every,interferences)
        ##### Simulation loop
        while True:
            # Synchronize non-blocking api calls
            for node in self.nodes:
                self.sync_node_non_blocking(node)
            # Synchronize blocking api calls
            for node in self.nodes:
                self.sync_node_blocking(node)
            # Simulation end
            if len(self.events) <= 0 or len(self.events) == 1 and self.events[0,0] == 3:
                # Notify nodes that wait for the end of the simulation
                # Note that we do not allow them to create new events (even if they try, they will not be processed)
                for node in self.nodes:
                    if node["state"] != "terminated":
                        node["state"]="running"
                        node.rqueue.put(("sim_end",RCode.SUCCESS))
                        self.sync_node_non_blocking(node) # Allow them for make non-blocking call requests (printing logs for example)
                    else:
                        node.rqueue.put(("sim_end",RCode.SUCCESS))
                break # End the event processing loop
            # Generate debug logs
            if debug:
                self.debug.debug()
            # Update simulation time
            self.time=self.events[0,1]
            self.time_truncated=format(self.time,self.precision) # refresh truncated time

            # Process events
            while len(self.events) > 0 and self.events[0,1] == self.time:
                event=self.events[0]     # Next event (self.events is sorted by timestamp and priorities)
                event_type=int(event[0]) # Event type
                ts=event[1]              # Timestamp
                content=event[2]         # Event content
                self.events=np.delete(self.events,0,0) # Consume events NOW! not at the end of the loop (event list may change in between)
                if event_type == 0:
                    src_id,dst_id,interface, data, datasize,duration,datasize_remaining,start_at,perform_delivery,receiver_required=content
                    src=self.nodes[int(src_id)]
                    dst=self.nodes[int(dst_id)]                    
                    if self.netmat[interface]["is_wired"]:
                        if perform_delivery:
                            dst["interfaces"][interface].put((data,start_at,self.time))
                            dst["interfaces_queue_size"][interface]+=1
                            self.log("Receive "+str(datasize)+" bytes on "+interface,node=int(dst_id))
                            # If node is receiving makes it consume (this way if there is a timeout, it will be removed!)
                            if dst["state"] == "call_blocking" and dst["request"] == "receive":
                                dst["interfaces_queue_size"][interface]-=1
                                dst["state"]="running"
                                dst.rqueue.put(("receive",RCode.SUCCESS))
                                self.sync_node_non_blocking(dst,timeout_remove_only=True)
                            self.notify_node_plugins(dst, "on_communication_end", event)
                        self.update_sharing(dst.node_id,-1,interface)
                        src["state"]="running"
                        code=RCode.SUCCESS if perform_delivery else RCode.FAIL
                        src.rqueue.put(("send",code))
                        self.sync_node_non_blocking(src,timeout_remove_only=True)
                        self.notify_node_plugins(src, "on_communication_end", event)
                    else:
                        if src.node_id != dst.node_id:
                            if perform_delivery:
                                dst["interfaces"][interface].put((data,start_at,self.time))
                                dst["interfaces_queue_size"][interface]+=1
                                self.log("Receive "+str(datasize)+" bytes on "+interface,node=int(dst_id))
                                # If node is receiving makes it consume (this way if there is a timeout, it will be removed!)
                                if dst["state"] == "call_blocking" and dst["request"] == "receive":
                                    dst["interfaces_queue_size"][interface]-=1
                                    dst["state"]="running"
                                    dst.rqueue.put(("receive",RCode.SUCCESS))
                                    self.sync_node_non_blocking(dst,timeout_remove_only=True)
                                self.notify_node_plugins(dst, "on_communication_end", event)
                        else:
                            src["state"]="running"
                            src.rqueue.put(("send",RCode.SUCCESS))
                            self.sync_node_non_blocking(src,timeout_remove_only=True)
                            self.notify_node_plugins(src, "on_communication_end", event)
                elif event_type == 1: # Timeout
                    node=self.nodes[int(content)]
                    node["state"]="running"
                    node.rqueue.put(("timeout",RCode.SUCCESS))
                    self.sync_node_non_blocking(node,timeout_remove_only=True)
                elif event_type == 4:
                    node=self.nodes[int(content)]
                    node["state"]="running"
                    node.rqueue.put(("notify",RCode.SUCCESS))
                    self.sync_node_non_blocking(node,timeout_remove_only=True)
                elif event_type == 2 or event_type == 3:
                    breakpoint_callback(self)
                    if event_type == 3:
                        self.add_event(3,self.time+breakpoints_every,0,1)                        
                
        ##### Simulation ends
        self.log("Simulation ends")

        ##### Final debug call
        if debug:
            self.debug.debug()
