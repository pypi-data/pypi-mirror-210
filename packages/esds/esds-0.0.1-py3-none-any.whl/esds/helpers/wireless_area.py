import math
import numpy as np

# This plugin is outdated
class WirelessArea:
    
    def __init__(self):
        self.nodes=list()

    def dump_nodes(self):
        i=0
        for node in self.nodes:
            x,y,z,com_range=node
            print("Node {} at ({},{},{}) with a communication range of {}m".format(i,x,y,z,com_range))
            i+=1
            
    def dump_infos(self):
        print("Number of nodes {}".format(len(self.nodes)))
        adjacency=self.generate_adjacency_matrix(fill_diagonal=False)
        print("Nodes average degree is {}".format(np.mean(np.sum(adjacency,axis=0))))
        x = [node[0] for node in self.nodes]
        y = [node[1] for node in self.nodes]
        z = [node[2] for node in self.nodes]
        com_range = [node[3] for node in self.nodes]
        print("Nodes locations ranges: x in [{},{}] y in [{},{}] z in [{},{}]".format(min(x),max(x),min(y),max(y),min(z),max(z)))
        print("Node communication ranges in [{},{}]".format(min(com_range),max(com_range)))      
        
    def add_node(self,x,y,z,com_range):
        self.nodes.append((x,y,z,com_range))

    def get_neighbours(self,node_id):
        node=self.nodes[node_id]
        neighbours=list()
        for i in range(0,len(self.nodes)):
            if i != node_id:
                neighbour=self.nodes[i]
                if math.dist(node[0:3],neighbour[0:3]) <= node[3]:
                    neighbours.append(i)
        return neighbours

    def generate_dot(self,filepath):
        is_strict=False
        com_range=self.nodes[0][3]
        for node in self.nodes:
            if node[3] != com_range:
                is_strict=True
                break
            
        with open(filepath, "w") as f:
            if is_strict:
                f.write("digraph G {\n")
            else:
                f.write("strict graph G {\n")
            for i in range(0,len(self.nodes)):
                neighbours=self.get_neighbours(i)
                for n in neighbours:
                    if is_strict:
                        f.write("{}->{}\n".format(i,n))
                    else:
                        f.write("{}--{}\n".format(i,n))
            f.write("}")
    
    def generate_adjacency_matrix(self,fill_diagonal=True):
        matrix=np.full((len(self.nodes),len(self.nodes)),0)
        if fill_diagonal:
            np.fill_diagonal(matrix,1) # Required by ESDS
        for i in range(0,len(self.nodes)):
            neighbours=self.get_neighbours(i)
            for n in neighbours:
                matrix[i,n]=1
        return matrix
        
