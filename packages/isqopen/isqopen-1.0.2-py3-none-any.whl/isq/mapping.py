import networkx as nx
from .errors import *
import random

single_gate = ['H', 'X', 'Y', 'Z', 'S', 'T', 'SD', 'TD', 'X2M', 'X2P', 'Y2M', 'Y2P', 'M']
multi_gate = ['CZ', 'CY', 'CX', 'CNOT']
theta_gate = ['RX', 'RY', 'RZ']

def get_init_map_by_reverse(qubit_num, topo, qcis):
    # get init map by reverse circuit and run mapping
    qcis_ir_list = qcis.split('\n')
    qcis_ir_list.reverse()
    qcis_reverse = "\n".join(qcis_ir_list)
    
    qcis_init = "{}\n{}".format(qcis, qcis_reverse)
    x = list(range(1, qubit_num+1))
    random.shuffle(x)
    init_map = [0]
    init_map.extend(x)

    mp = Map(qubit_num, topo, qcis_init, init_map)
    mp.mapping()
    return mp.log_to_phy

# simplified sabre mapping 
class Map:

    def __init__(self, qubit_num: int, topo: [[int]], qcis: str, init_map = None, debug = False):

        self.debug = debug

        # some constant parameter
        self.W = 0.3
        self.extended_number = 5

        # qubit number
        self.qubit_num = qubit_num

        # build chip
        self.ag = self.chip_build(qubit_num, topo)
        
        # get gate topo graph and front layer
        self.front = set()
        self.extended = set()
        self.dg = self.qcis_parse(qcis)
        self.get_extended()
        
        # qbit mapping list
        self.log_to_phy = list(range(qubit_num+1)) 
        self.phy_to_log = list(range(qubit_num+1))
        if init_map:
            for l, p in enumerate(init_map):
                self.log_to_phy[l] = p
                self.phy_to_log[p] = l
        
        self.exec = []

    def mapping(self):
        
        # exec single gate before front layer first
        for gate in self.dg.single_gates_before:
            self.print_normal(gate)

        while self.front:
            
            exec_list = self.get_executable()
            
            if exec_list:
                for node in exec_list: self.execute(node)
                self.get_extended()
            else:
                best_swap = self.get_best_swap()
                self.exec_swap(best_swap)
        
        for ms in self.dg.measure:
            self.print_normal(ms)

        return '\n'.join(self.exec)
    
    def exec_swap(self, swap):
        p1, p2 = swap
        l1, l2 = self.phy_to_log[p1], self.phy_to_log[p2]
        #self.print_normal(('SWAP', [l1, l2]))
        # swap 
        self.print_normal(('Y2P', [l2]))
        self.print_normal(('CZ', [l1, l2]))
        self.print_normal(('Y2M', [l2]))
        self.print_normal(('Y2P', [l1]))
        self.print_normal(('CZ', [l2, l1]))
        self.print_normal(('Y2M', [l1]))
        self.print_normal(('Y2P', [l2]))
        self.print_normal(('CZ', [l1, l2]))
        self.print_normal(('Y2M', [l2]))
        
        self.log_to_phy[l1], self.log_to_phy[l2] = p2, p1
        self.phy_to_log[p1], self.phy_to_log[p2] = l2, l1

    def get_best_swap(self):
        swap_list = self.get_swaps()
        best_hs = float('inf')
        best_swap = None
        for swap in swap_list:
            # swap physical qubit
            p1, p2 = swap
            l1, l2 = self.phy_to_log[p1], self.phy_to_log[p2]
            self.log_to_phy[l1], self.log_to_phy[l2] = p2, p1
            self.phy_to_log[p1], self.phy_to_log[p2] = l2, l1
            # calc score
            fs = self.get_nnc_score(self.front)
            es = self.get_nnc_score(self.extended)
            hs = fs + self.W * es
            if hs < best_hs:
                best_hs = hs
                best_swap = swap
            #recover swap
            self.log_to_phy[l1], self.log_to_phy[l2] = p1, p2
            self.phy_to_log[p1], self.phy_to_log[p2] = l1, l2

        return best_swap

    # get nnc socre
    def get_nnc_score(self, node_list):
        nnc = 0.0
        for node in node_list:
            l1, l2 = self.dg.nodes[node]['gate'][1]
            p1, p2 = self.log_to_phy[l1], self.log_to_phy[l2]
            nnc += self.ag.D[p1][p2]
        if len(node_list) > 0: nnc /= len(node_list)
        return nnc

    # get potential swap list
    def get_swaps(self):
        swap_list = []
        for node in self.front:
            l1, l2 = self.dg.nodes[node]['gate'][1]
            p1, p2 = self.log_to_phy[l1], self.log_to_phy[l2]
            for nxt in self.ag.neighbors(p1):
                swap_list.append((p1, nxt))
            for nxt in self.ag.neighbors(p2):
                swap_list.append((p2, nxt))
        return swap_list

    # execute gate in front layer
    def execute(self, node):
        self.print_normal(self.dg.nodes[node]['gate'])
        for gate in self.dg.nodes[node]['single_gates0']: self.print_normal(gate)
        for gate in self.dg.nodes[node]['single_gates1']: self.print_normal(gate)
        # remove from front layer
        self.front.remove(node)
        nxt_list = list(self.dg.successors(node))
        for nxt in nxt_list:
            # remove edge from dg, if next node's in degree is 0, add to front layer
            self.dg.remove_edge(node, nxt)
            if self.dg.in_degree(nxt) == 0:
                self.front.add(nxt)
                if nxt in self.extended: self.extended.remove(nxt)

    # get executable node from front layer
    def get_executable(self):
        exec_list = set()
        
        for node in self.front:
            l1, l2 = self.dg.nodes[node]['gate'][1]
            p1, p2 = self.log_to_phy[l1], self.log_to_phy[l2]
            if self.ag.D[p1][p2] == 1:
                exec_list.add(node)              
        return exec_list

    # look ahead, get some extended nodes
    def get_extended(self):
        now_layer = self.front
        while len(self.extended) < self.extended_number:
            next_layer = self.get_next_layer(now_layer)
            if len(next_layer) == 0: break
            self.extended = set.union(self.extended, next_layer)
            now_layer = next_layer

    # get next layer's nodes from dg
    def get_next_layer(self, now_layer):
        next_layer = set()
        for node in now_layer:
            for nxt in self.dg.successors(node):
                next_layer.add(nxt)
        return next_layer
    
    # build chip graph
    def chip_build(self, qubit_num: int, topo: [[int]]):

        ag = nx.Graph()
        ag.add_nodes_from(range(1, qubit_num))
        for s, e in topo:
            ag.add_edge(s, e)
        ag.D = dict(nx.shortest_path_length(ag), method = 'dijkstra')
        
        # all nodes need to be connected
        for i in ag.D:
            if len(ag.D[i]) < self.qubit_num: ThrowMappingError('all nodes need to be connected')
            break
        
        return ag
    
    # parse qcis, build gate's topo graph: dg
    def qcis_parse(self, qcis):

        dg = nx.DiGraph()
        dg.single_gates_before = []
        dg.measure = []
        
        pre_nodes = [-1]*(self.qubit_num+1)

        for idx, qcis_ir in enumerate(qcis.split('\n')):
            ir = qcis_ir.strip()
            if not ir: continue
            normal = self.qcis_normalize(idx+1, ir)

            if normal[0] == 'M':
                dg.measure.append(normal)
                continue

            if len(normal[1]) == 1:
                qubit = normal[1][0]
                node = pre_nodes[qubit]
                if node == -1:
                    dg.single_gates_before.append(normal)
                else:
                    if qubit == dg.nodes[node]['gate'][1][0]:
                        dg.nodes[node]['single_gates0'].append(normal)
                    else:
                        dg.nodes[node]['single_gates1'].append(normal)
            else:
                dg.add_node(idx, gate=normal, single_gates0=[], single_gates1=[])
                haspre = False
                for qid in normal[1]:
                    if pre_nodes[qid] != -1:
                        dg.add_edge(pre_nodes[qid], idx)
                        haspre = True
                    pre_nodes[qid] = idx
                
                if not haspre: self.front.add(idx)

        return dg
    
    def print_normal(self, normal):

        q1 = self.log_to_phy[normal[1][0]]
        qcis = "{} Q{}".format(normal[0], q1)
        if len(normal[1]) == 2:
            q2 = self.log_to_phy[normal[1][1]]
            qcis = "{} Q{}".format(qcis, q2)
        if len(normal) == 3:
            qcis = "{} {}".format(qcis, normal[2])

        self.exec.append(qcis)



    def qcis_normalize(self, line_id, qcis_ir):
        
        ir_item = qcis_ir.split(' ')
        
        if len(ir_item) < 2: ThrowMappingError('in line {}, qcis ir is illegal'.format(line_id))
        if ir_item[1][0] != 'Q' or not ir_item[1][1:].isdigit(): ThrowMappingError('in line {}, qubit format error'.format(line_id))
        qid1 = int(ir_item[1][1:])
        
        if qid1 > self.qubit_num: ThrowMappingError('in line {}, qubit number out of range'.format(line_id))

        if (ir_item[0] in single_gate):
            if len(ir_item) != 2: ThrowMappingError('in line {}, qcis ir is illegal'.format(line_id))
            return (ir_item[0], [qid1])
        elif (ir_item[0] in multi_gate):
            if len(ir_item) != 3: ThrowMappingError('in line {}, qcis ir is illegal'.format(line_id))
            if ir_item[2][0] != 'Q' or not ir_item[2][1:].isdigit(): ThrowMappingError("in line {}, qubit format error".format(line_id))
            qid2 = int(ir_item[2][1:])
            if qid2 > self.qubit_num: ThrowMappingError('in line {}, qubit number out of range'.format(line_id))
            return (ir_item[0], [qid1, qid2])
        elif (ir_item[0] in theta_gate):
            if len(ir_item) != 3: ThrowMappingError('in line {}, qcis ir is illegal'.format(line_id))
            for sd in ir_item[2].split('.'):
                if not sd.isdigit(): ThrowMappingError('in line {}, angle need a float point number'.format(line_id))
            return (ir_item[0], [qid1], float(ir_item[2]))
        else:
            ThrowMappingError('in line {}, gate is not supported in qcis'.format(line_id))