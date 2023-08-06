#!/usr/bin/env python

from .node_plugin import NodePlugin

# PowerStates allows you to measure the energy consumption of a
# node that go through several power states during the simulation
# Two version of Powerstates is provided by mean of two classes:
#   - Powerstates: Allow you to set the node power consumption to arbitraries values
#   - PowerstatesFromFile: Allow you to set the node power consumption from power values defined in a file

######################
#     _    ____ ___  #
#    / \  |  _ \_ _| #
#   / _ \ | |_) | |  #
#  / ___ \|  __/| |  #
# /_/   \_\_|  |___| #
#                    #
######################

# #Regarding PowerStates:
# import Powerstates as ps
# pstates=ps.PowerStates(<api>,<power_init>)
# pstates.set_power(<power>) # Switch the power consumption to <power>
# pstates.report_energy() # Display the current node energy consumption up to the current simulated time
# pstates.report_power_changes() # Display all the power changes up to the current simulated time

# #Regarding PowerStatesFromFile:
# #Format of <file> is one <entry> per line that follow this format <state-0>:<state-1>:...:<state-n>
# #Each line can corresponds to one node (line 0 for node 0 etc..)
# import Powerstates as ps
# pstates=ps.PowerStatesFromFile(<api>,<file>,<entry-line>) # Create a power states on a node that uses <api> using line <entry-line> of file <file>
# pstates.set_state(<id>) # Switch to the <id> power states
# pstates.report_energy() # Display the current node energy consumption up to the current simulated time
# pstates.report_power_changes() # Display all the power changes up to the current simulated time
# pstates.report_state_changes() # Display all the states changes up to the current simulated time


class PowerStates(NodePlugin):
    """
    PowerStates model the energy consumed by the various changes of power consumption of a node over time.
    """
    def __init__(self,api,power_init):
        super().__init__("Powerstates",api)
        self.clock=self.api.read("clock")
        self.energy=0
        self.power=power_init
        self.power_changes=dict()
        self.set_power(power_init)
        

    def set_power(self,power_watt):
        cur_clock=self.api.read("clock")
        self.energy+=self.power*(cur_clock-self.clock)
        self.clock=cur_clock
        if self.power != power_watt:
            self.power_changes[cur_clock]=power_watt
        self.power=power_watt
        return cur_clock

    def report_energy(self):
        self.set_power(self.power)
        self.log("Consumed "+str(self.energy) +"J")
        
    def report_power_changes(self):
        self.set_power(self.power)
        for key in self.power_changes.keys():
            self.log("At t="+str(key)+" power is "+str(self.power_changes[key])+"W")



class PowerStatesFromFile(PowerStates):
    """
    A version of Powerstates that load the power values from a file.
    """
    def __init__(self,api,state_file,entry_line=1):
        self.state_changes=dict()
        self.states=[]
        self.state=0
        with open(state_file) as fp:
            for i, line in enumerate(fp):
                if i+1 == entry_line:
                    self.states=line.split(":")
                    self.states=[float(i) for i in self.states]
        assert len(self.states) > 0
        super().__init__(api,self.states[0])
        self.set_state(0)

    def set_state(self,state_id):
        assert state_id < len(self.states)
        clock=super().set_power(self.states[state_id])
        if self.state != state_id:
            self.state_changes[clock]=state_id
        self.state=state_id


    def report_state_changes(self):
        self.set_state(self.state)
        for key in self.state_changes.keys():
            self.log("At t="+str(key)+" state is "+str(self.state_changes[key]))

        
class PowerStatesComms(NodePlugin):
    """
    Monitor the energy consumed by the network interfaces by mean of power states.
    Note that for finer grained predictions, bytes and packet power consumption must be accounted.
    Which is not the case with these power states.
    """

    def __init__(self,api):
        super().__init__("PowerStatesComms",api)
        self.power=dict() # Store each interface informations

    def on_communication_end(self,time,com_event):
        content=com_event[2]
        dataSize=content[4]
        duration=time-content[7]
        interface=content[2]
        mode= "tx" if content[0] == self.api.node_id else "rx"
        self.power[interface]["consumption_dynamic"]+=self.power[interface][mode]*duration

    def set_power(self,interface,idle,tx,rx):
        self.power[interface]=dict()
        self.power[interface]["idle"]=idle
        self.power[interface]["rx"]=rx
        self.power[interface]["tx"]=tx
        self.power[interface]["on_at"]=self.api.read("clock")
        self.power[interface]["consumption_idle"]=0
        self.power[interface]["consumption_dynamic"]=0

    def on_turn_on(self):
        for interface in self.power.keys():
            self.power[interface]["on_at"]=self.api.read("clock")
    
    def on_turn_off(self):
        self.sync_idle()

    def sync_idle(self):
        clock=self.api.read("clock")
        for interface in self.power.keys():
            self.power[interface]["consumption_idle"]+=(clock-self.power[interface]["on_at"])*self.power[interface]["idle"]
            self.power[interface]["on_at"]=clock
    
    def get_energy(self):
        self.sync_idle()
        consumption=0
        for interface in self.power.keys():
            consumption+=self.power[interface]["consumption_idle"]+self.power[interface]["consumption_dynamic"]
        return consumption

    def get_idle(self,interface):
        self.sync_idle()
        return(self.power[interface]["consumption_idle"])
  
    def report_energy(self):
        self.log("Communications consumed "+str(round(self.get_energy(),2))+"J")
