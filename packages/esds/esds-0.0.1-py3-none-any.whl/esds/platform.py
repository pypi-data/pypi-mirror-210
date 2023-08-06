
import yaml, os, importlib
import numpy as np
from .simulator import Simulator

class UnitsParser:
    def node_range(r,limit):
        if r == "all":
            return(range(0,limit))
        r=r.replace("@",str(limit-1))
        elt=r.split("-")
        if len(elt) == 2:
            min = int(elt[0])
            max = int(elt[1])
            if min < 0 or max >= limit:
                raise Exception("Outside of range limit [0-"+str(limit)+"]")
            return(range(min,max+1))
        else:
            return(list(map(int, r.split(","))))

    def bandwidth(bw):
        for i,c in enumerate(bw):
            if not c.isdigit() and c != ".":
                break
        number=float(bw[:i])
        unit=bw[i:]
        number=number*1000*1000 if unit == "Mbps" else number
        number=number*1000*1000*8 if unit == "MBps" else number
        number=number*1000 if unit == "kbps" else number
        number=number*1000*8 if unit == "kBps" else number
        number=number*8 if unit == "Bps" else number
        return(number)

    def latency(lat):
        for i,c in enumerate(lat):
            if not c.isdigit() and c != ".":
                break
        number=float(lat[:i])
        unit=lat[i:]
        number=number*60 if unit in ["m","M"] else number
        number=number*3600 if unit in ["h","H"] else number
        number=number/1000 if unit in ["ms","MS"] else number
        return(number)

class YAMLPlatformFile:

    def __init__(self, file_path):
        self.file_path=file_path
        self.location=os.path.dirname(os.path.abspath(file_path))
        self.default={
            "breakpoints": [],
            "breakpoints_every": None,
            "breakpoints_file": None,
            "breakpoints_callback": lambda s:None,
            "debug": False,
            "debug_file": "./esds.debug",
            "interferences": True,
            "node_count": 0,
            "implementations": [],
            "arguments": [],
            "interfaces": dict()
        }

        with open(file_path) as f:
            self.platform = yaml.load(f, Loader=yaml.FullLoader)

        ##### General
        if "general" in self.platform:
            self.parse_general()
        ##### Nodes
        if "nodes" in self.platform:
            self.parse_nodes()
        else:
            self.parsing_error("platform file has no nodes section")
        ##### Interfaces
        if "interfaces" in self.platform:
            self.parse_interfaces()
        else:
            self.parsing_error("platform file has no interfaces section")

        ##### Sanity checks
        if None in self.default["implementations"]:
            self.parsing_error("Some nodes do not have assigned implementation")

    def parsing_error(self,msg):
        raise Exception("Fail to parse platform file \""+self.file_path+"\": "+msg)

    def parse_link(self,link):
        words=link.split()
        if len(words) == 4:
            return((
                UnitsParser.node_range(words[0],self.default["node_count"]),
                UnitsParser.bandwidth(words[1]),
                UnitsParser.latency(words[2]),
                UnitsParser.node_range(words[3],self.default["node_count"])))
        self.parsing_error("Invalide link \""+link+"\"")

    def parse_txperf(self,txperf):
        elts=txperf.split()
        return((UnitsParser.node_range(elts[0],self.default["node_count"]),UnitsParser.bandwidth(elts[1]),UnitsParser.latency(elts[2])))

    def parse_interfaces(self):
        interfaces=self.platform["interfaces"]
        node_count=self.default["node_count"]
        for i in interfaces:
            if interfaces[i]["type"] not in ["wireless","wired"]:
                self.parsing_error("Invalid interface type \""+interfaces[i]["type"]+"\"")
            is_wired=interfaces[i]["type"] == "wired"
            links=list()
            if type(interfaces[i]["links"]) != list:
                self.parsing_error("Invalide type of links in interface "+i)
            for link in interfaces[i]["links"]:
                links.append(self.parse_link(link))
            ##### Create network matrix
            BW=np.full((node_count,node_count),0)
            LAT=np.full((node_count,node_count),0)
            for link in links:
                for n1 in link[0]:
                    for n2 in link[3]:
                        BW[n1][n2]=link[1]
                        LAT[n1][n2]=link[2]

            ##### Set txperfs for wireless interfaces
            if not is_wired:
                txperfs=interfaces[i]["txperfs"]
                for txperf in txperfs:
                    p=self.parse_txperf(txperf)
                    for node in p[0]:
                        BW[node][node]=p[1]
                        LAT[node][node]=p[2]
                if (BW.diagonal()==0).any():
                    self.parsing_error("Not all node have a txpref on the wireless interface "+i)

            self.default["interfaces"][i]={
                "is_wired": is_wired,
                "bandwidth": BW,
                "latency": LAT
            }

    def parse_nodes(self):
        nodes=self.platform["nodes"]
        if "count" in nodes:
            if not str(nodes["count"]).isnumeric():
                self.parsing_error("node count should be a number")
            self.default["node_count"]=nodes["count"]
        else:
            self.parsing_error("node count not provided")
        if "implementations" in nodes:
            if type(nodes["implementations"]) != list:
                self.parsing_error("nodes implementations should be a list of file path")
            self.default["implementations"]=[None]*self.default["node_count"]
            for impl in nodes["implementations"]:
                words=impl.split()
                r=UnitsParser.node_range(words[0],self.default["node_count"])
                file="".join(words[1:])
                if not os.path.exists(os.path.join(self.location,file)):
                    self.parsing_error("File "+file+ " not found")
                path, extension = os.path.splitext(file)
                if extension != ".py":
                    self.parsing_error("File "+file+" must be a python file")
                for node in r:
                    self.default["implementations"][node]=path
        else:
            self.parsing_error("node implementation not provided")
        ##### Nodes arguments
        self.default["arguments"]=[None]*self.default["node_count"]
        if "arguments" in nodes:
            args=nodes["arguments"]
            for r in args:
                for node_id in UnitsParser.node_range(str(r),self.default["node_count"]):
                    self.default["arguments"][node_id]=args[r]

    def parse_general(self):
        general=self.platform["general"]
        if "breakpoints" in general:
            if type(general["breakpoints"]) != list:
                self.parsing_error("breakpoints should be a list of number")
            self.default["breakpoints"]=general["breakpoints"]
        if "breakpoints_every" in general:
            self.default["breakpoints_every"]=float(general["breakpoints_every"])
        if "breakpoints_callback" in general:
            cb=general["breakpoints_callback"]
            file=cb["file"]
            path, ext=os.path.splitext(file)
            if not os.path.exists(os.path.join(self.location,file)):
                self.parsing_error("File "+file+ " not found")
            path, extension = os.path.splitext(file)
            if extension != ".py":
                self.parsing_error("File "+file+" must be a python file")
            self.default["breakpoints_file"]=cb["file"]
            self.default["breakpoints_callback"]=cb["callback"]
        if "debug" in general:
            if type(general["debug"]) != bool:
                self.parsing_error("debug should be on or off")
            self.default["debug"]=general["debug"]
        if "debug_file" in general:
            self.default["debug_file"]=general["debug_file"]
        if "interferences" in general:
            if type(general["interferences"]) != bool:
                self.parsing_error("interferences should be on or off")
            self.default["interferences"]=general["interferences"]

    def run(self):
        ##### First load callback from file if any
        if self.default["breakpoints_file"] != None:
            module, ext=os.path.splitext(self.default["breakpoints_file"])
            imported=importlib.import_module(module)
            callback=getattr(imported, self.default["breakpoints_callback"])
            self.default["breakpoints_callback"]=callback
        ##### Create simulator
        simulator=Simulator(self.default["interfaces"])
        for node_id in range(0,self.default["node_count"]):
            simulator.create_node(self.default["implementations"][node_id], args=self.default["arguments"][node_id])
        ##### Run simulation
        simulator.run(
            breakpoints=self.default["breakpoints"],
            breakpoints_every=self.default["breakpoints_every"],
            breakpoint_callback=self.default["breakpoints_callback"],
            debug=self.default["debug"],
            debug_file_path=self.default["debug_file"],
            interferences=self.default["interferences"])
        