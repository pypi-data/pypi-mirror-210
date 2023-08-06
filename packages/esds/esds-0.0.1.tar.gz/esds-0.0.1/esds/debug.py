import sys,time,json
import numpy as np
import esds

def serialize_int64(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError ("Type %s is not serializable" % type(obj))

class Debug:
    def __init__(self, simulator, file_path, breakpoints,breakpoints_every,interferences):
        self.simulator=simulator
        self.file_path=file_path
        self.loop_count=0
        self.logs=list()
        header={
            "debug_version": 1,
            "python_version": sys.version,
            "esds_version": esds.__version__,
            "simulation_started_at": simulator.startat,
            "number_of_nodes": len(simulator.nodes),
            "manual_breakpoints": breakpoints,
            "auto_breakpoint": breakpoints_every,
            "interferences": interferences
        }
        self.write(header,append=False)

    def append_log(self,log):
        self.logs.append(log)

    def write(self,data, append=True):
        mode="a" if append else "w"
        with open(self.file_path, mode) as f:
            f.write(json.dumps(data,default=serialize_int64,separators=(",",":")))
            f.write("\n")

    def get_network_interfaces(self):
        data=dict()
        for interface in self.simulator.netmat:
            data[interface]={ 
                "is_wired":self.simulator.netmat[interface]["is_wired"],
                "bandwidth": self.simulator.netmat[interface]["bandwidth"].tolist(),
                "latency": self.simulator.netmat[interface]["latency"].tolist(),
            }
            if self.simulator.netmat[interface]["is_wired"]:
                data[interface]["sharing"]=self.simulator.sharing[interface].tolist()

        return(data)
    
    def get_events_list(self):
        events=list()
        for event_numpy in self.simulator.events:
            event_id=event_numpy[0]
            content=event_numpy[2].tolist()
            final_content=dict()
            if event_id == 0:
                final_content={
                    "src": content[0],
                    "dst": content[1],
                    "interface": content[2],
                    "datasize":content[4],
                    "duration":content[5],
                    "datasize_remaining": content[6],
                    "start_timestamp":content[7],
                    "perform_delivery":content[8],
                    "receiver_required":content[9]
                }
            elif event_id == 1:
                final_content={
                    "node": content
                }
            elif event_id == 4:
                final_content={
                    "node": content
                }       
            event={
                "id": event_id,
                "ts": event_numpy[1],
                "priority": event_numpy[3],
                "content": final_content,
            }
            events.append(event)
        return(events)
    
    def get_nodes_infos(self):
        nodes_infos=list()
        for node in self.simulator.nodes:
            node_info = {
                "turned_on": node["turned_on"]
            }
            nodes_infos.append(node_info)
        return(nodes_infos)

    def debug(self):
        """
        Log all the informations for debugging
        """
        self.loop_count+=1
        loop_data={
            "loop_count": self.loop_count,
            "started_since": round(time.time()-self.simulator.startat,2),
            "simulated_time": float(self.simulator.time_truncated),
            "simulated_time_accurate": self.simulator.time,
            "network_interfaces": self.get_network_interfaces(),
            "events_list": self.get_events_list(),
            "nodes_infos": self.get_nodes_infos(),
            "logs": self.logs
        }
        self.write(loop_data)
        self.logs.clear()
