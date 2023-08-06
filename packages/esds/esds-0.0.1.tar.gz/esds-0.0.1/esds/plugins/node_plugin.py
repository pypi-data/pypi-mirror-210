class NodePlugin:
    """
    Node plugins get register to the node API get notified when events occurs.
    The call and return suffixes are used for methods that are called at the beginning
    and the end, respectively, of API calls triggered by the node source code.

    Changing this API could brake most of the node plugins.
    """

    def __init__(self,plugin_name,api):
        self.api=api
        self.plugin_name=plugin_name
        api.plugin_register(self)

    def on_send_call(self,interface,data,datasize,dst):
        pass

    def on_send_return(self,interface,data,datasize,dst,code):
        pass

    def on_receive_return(self,interface,data,start_at,end_at):
        pass
    
    def on_terminated(self):
        pass

    def on_communication_end(self,time,com_event):
        pass
    
    def on_turn_on(self):
        pass

    def on_turn_off(self):
        pass

    def log(self,msg):
        self.api.log(self.plugin_name+"(NP) "+msg)

