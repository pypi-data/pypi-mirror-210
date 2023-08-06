import matplotlib.pyplot as plt
from matplotlib import patches
from collections import defaultdict

single_gate = ['H', 'X', 'Y', 'Z', 'S', 'T', 'SD', 'TD', 'X2M', 'X2P', 'Y2M', 'Y2P', 'M']
multi_gate = ['CZ', 'CY', 'CX', 'CNOT']
theta_gate = ['RX', 'RY', 'RZ']

def normalize(isq_ir):
    ir_item = isq_ir.split(' ')
    qid1 = int(ir_item[1][1:])-1    
    if (ir_item[0] in single_gate):
        return (ir_item[0], [qid1])
    elif (ir_item[0] in multi_gate):
        qid2 = int(ir_item[2][1:])-1
        return (ir_item[0], [qid1, qid2])
    elif (ir_item[0] in theta_gate):
        return (ir_item[0], [qid1], ir_item[2])

def sequence(isq_ir):

    node_time = defaultdict(int)
    seq_time = 0
    seqs = defaultdict(list)
    seqs_width = defaultdict(int)
    qubit_set = set()
    for ir in isq_ir.split('\n'):
        normal = normalize(ir)
        if len(normal[1]) == 1:
            qubit = normal[1][0]
            t = node_time[qubit]
            seqs[t].append(normal)
            node_time[qubit] = t+1
            seq_time = max(seq_time, t)
            qubit_set.add(qubit)
            seqs_width[t] = max(seqs_width[t], 1)
            if normal[0] in theta_gate:
                w = len(normal[2]) // 3 + 2
                seqs_width[t] = max(seqs_width[t], w)
        else:
            q1, q2 = normal[1]
            t1, t2 = node_time[q1], node_time[q2]
            t = max(t1, t2)
            seqs[t].append(normal)
            node_time[q1] = t+1
            node_time[q2] = t+1
            seq_time = max(seq_time, t)
            qubit_set.add(q1)
            qubit_set.add(q2)
            seqs_width[t] = max(seqs_width[t], 1)

    return seqs, seq_time, seqs_width, len(qubit_set)


class Drawer():

    def __init__(self, showparam = False) -> None:
        self.box_length = 0.5
        self.box_width = 0.5
        self.pad = 0.1
        self.ctrl_rad = 0.1
        self.circ_rad = 0.3
        self.showparam = showparam
    
    def plot(self, isq_ir):
        '''
        plot the circuit of isq/qcis ir
        '''
        seqs, seq_time, seqs_width, qnum = sequence(isq_ir)
        n = seq_time+1
        if self.showparam:
            for k in seqs_width:
                t = seqs_width[k]
                seq_time += (t-1) * 0.5
        
        self.fg = plt.figure(figsize=((seq_time+3)/2, (qnum+1)/2))
        self.ax = self.fg.add_axes(
            [0,0,1,1],
            xlim=(-1, seq_time + 2),
            ylim=(-1, qnum),
            xticks=[],
            yticks=[],
        )
    
        self.ax.axis("off")
        self.ax.invert_yaxis()
        
        # plot qubit lines
        line_options = {"color": "black", "linewidth": 2, "zorder": 1}
        for i in range(qnum):
            line = plt.Line2D((-1, seq_time+1), (i, i), **line_options)
            self.ax.add_line(line)
        
        center = 0
        for i in range(n):
            t = seqs_width[i]
            for norm in seqs[i]:
                # get sequence center
                seq_t = center
                if self.showparam: seq_t += (t-1) * 0.25
                if norm[0] == 'M':
                    self.measure(norm[1][0], seq_t)
                elif norm[0] in multi_gate:
                    self.ctrl_gate(norm[0], norm[1], seq_t)
                else:
                    self.single_gate(norm, seq_t, t)

            center += 1
            if self.showparam: center += (t-1) * 0.5

    def box(self, qubit, seq_t):
        '''
        build a box, whose width and height are 'box_width' and 'box_length'

        qubit: which box is build on
        seq_t: box center
        '''
        box_length = self.box_length
        box_width = self.box_width
        pad = self.pad

        x_loc = seq_t - box_width / 2.0 + pad
        y_loc = qubit - box_length / 2.0 + pad

        boxstyle = "round, pad=0.2"
        box_options = {'facecolor': 'white', 'edgecolor': 'black', 'linewidth': 2}

        box = patches.FancyBboxPatch(
            (x_loc, y_loc),
            box_width - 2 * pad,
            box_length - 2 * pad,
            boxstyle=boxstyle,
            **box_options
        )
        self.ax.add_patch(box)

    def single_gate(self, norm, seq_t, width = 1):
        '''
        build single gate

        norm: normalize ir
        seq_t: box center
        width: box width, default is 1, when need show rotation value, width maybe become large
        '''
        name = norm[0]
        qubit = norm[1][0]
        if self.showparam: self.box_width = width * 0.5
        self.box(qubit, seq_t)
        self.box_width = 0.5
        new_text_options = {"zorder": 3, "ha": "center", "va": "center", "fontsize": 12}
        if name in ['X2M', 'X2P', 'Y2M', 'Y2P']:
            new_text_options['fontsize'] = 10
        
        #when 'showparam' is set to True, then RX, RY, RZ will show the rotation value
        if self.showparam and name in theta_gate:
            new_text_options['fontsize'] = 10
            name = f'{norm[0]}({norm[2]})'
        self.ax.text(
            seq_t,
            qubit,
            name,
            **new_text_options
        )
    
    def ctrl_gate(self, name, qubit, seq_t):
        '''
        build ctrl gate

        name: gate name which in [CX, CY, CZ, CNOT]
        qubit: [q1, q2]
        seq_t: box center
        '''
        #ctrl node, build a black spot
        ctrl_rad = self.ctrl_rad
        options = {"color": "black", "linewidth": 2}
        circ_ctrl = plt.Circle((seq_t, qubit[0]), radius=ctrl_rad, **options)
        self.ax.add_patch(circ_ctrl)
        #target node, when CX or CNOT, build a circle and a '+', else build a single gate
        if (name == 'CX' or name == 'CNOT'):
            circ_rad = self.circ_rad
            new_options = {"facecolor": "white", "edgecolor": "black", "linewidth": 2}
            target_circ = plt.Circle((seq_t, qubit[1]), radius=circ_rad, **new_options)
            target_v = plt.Line2D((seq_t, seq_t), (qubit[1] - circ_rad, qubit[1] + circ_rad), **options)
            target_h = plt.Line2D((seq_t - circ_rad, seq_t + circ_rad), (qubit[1], qubit[1]), **options)
            self.ax.add_patch(target_circ)
            self.ax.add_line(target_v)
            self.ax.add_line(target_h)
            # ctrl line
            line = plt.Line2D((seq_t, seq_t), (qubit[0], qubit[1]), **options)
            self.ax.add_line(line)
        else:
            if name == 'CY':
                self.single_gate(('Y', [qubit[1]]), seq_t)
            else:
                self.single_gate(('Z', [qubit[1]]), seq_t)
            #ctrl line
            if qubit[1] > qubit[0]:
                line = plt.Line2D((seq_t, seq_t), (qubit[0], qubit[1] - self.box_length/2.0 - 1.5*self.pad), **options)
                self.ax.add_line(line)
            else:
                line = plt.Line2D((seq_t, seq_t), (qubit[0], qubit[1] + self.box_length/2.0 + self.pad), **options)
                self.ax.add_line(line)

    def measure(self, qubit, seq_t):
        '''
        build measure, which composed of a box, an arc and a arrow

        qubit: which measure is build on
        seq_t: box center
        '''
        self.box(qubit, seq_t)
        
        box_length = self.box_length

        arc_options = {"linewidth": 2}
        arc = patches.Arc(
            (seq_t, qubit + box_length / 10),
            0.6 * box_length,
            0.55 * box_length,
            theta1=180,
            theta2=0,
            **arc_options
        )
        self.ax.add_patch(arc)
        
        arrow_start_x = seq_t - 0.165 * box_length
        arrow_start_y = qubit + 0.25 * box_length
        arrow_width = 0.35 * box_length
        arrow_height = -0.55 * box_length

        arrow_options = {'facecolor': 'black', 'edgecolor': 'black', 'linewidth': 2}
        self.ax.arrow(
            arrow_start_x,
            arrow_start_y,
            arrow_width,
            arrow_height,
            head_width=box_length / 8.0,
            **arrow_options
        )