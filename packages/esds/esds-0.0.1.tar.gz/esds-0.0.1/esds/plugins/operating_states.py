#!/usr/bin/env python

from plugins.node_plugin import *

######################
#     _    ____ ___  #
#    / \  |  _ \_ _| #
#   / _ \ | |_) | |  #
#  / ___ \|  __/| |  #
# /_/   \_\_|  |___| #
#                    #
######################

# import plugins.operating_states as op
# # Load the directional transition graph from graph.txt starting at the "vertex1" state
# opstate=op.OperatingStates(api,"graph.txt","vertex1")
# Format of the graph.txt file consists in one edge per line
# that consists on the source vertex and destination vertex sperated by a space
# As an example: 
# vertex1 vertex2
# vertex1 vertex3
# vertex3 vertex2
# vertex2 vertex1
# 
# opstate.register_callback(boom) 
# # On each state transition boom will be called as boom(src_state,dst_state)
# # This way the boom callback can contains power_state transitions for examples 
# opstate.goto("vertex2") # works
# opstate.goto("vertex3") # wont work
# opstate.goto("vertex1") # work since we are on vertex2

class OperatingStates(NodePlugin):
    """
    OperatingStates plugin
    """
    def __init__(self,api, state_file, initial_state):
        self.transitions=list()
        self.callbacks=list()
        self.state=initial_state
        with open(state_file) as fp:
            for i, line in enumerate(fp):
                self.transitions.append(line)
        super().__init__("OperatingStates",api)

    def goto(self,state):
        if (self.state+" "+state) in self.transitions:
            old_state=self.state
            self.state=state
            for c in self.callbacks:
                c(old_state,state)
        else:
            self.log("Invalid transition "+self.state+" => "+state)

    def get_state(self):
        return(self.state)
    
    def register_callback(self,callback):
        """
            The callback will be called on each state transition
            Callback takes two arguments which are:
             - The source state
             - The destination state
        """
        self.callbacks.append(callback)


