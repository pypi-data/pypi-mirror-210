from .qtypes import *
import typing as T
import copy
from isq.errors import *
import numpy as np
import time
from .tools import decompose

"""
Flatten defBlock into a list of definitions.
This makes qbitDef children Tuple[var_array|var] -> List[var_array|var]
"""
'''
def flatten_qbitdef_list(s: Node)->Node:
    defs = T.cast(Node, s.children[0])
    for d in defs.children:
        if(d.type == 'qbitDef'):
            flattened_def=[]
            var_def = T.cast(Node, d.children[0])
            while var_def.children != []:
                next_node = var_def.children[0]
                var_def.children=[]
                flattened_def.append(var_def)
                var_def=next_node
            flattened_def.append(var_def)
            flattened_def.reverse()
            d.children = flattened_def
    return s
'''

QubitRef = T.Union[str, T.Tuple[str, int]]

def wrapInt(q: int)->Node:
    return Node("intExprLiteral", [], q)
def wrapQubitRef(q: QubitRef)->Node:
    if isinstance(q, str):
        return Node("qubitSingleRef", [], q)
    else:
        return Node("qubitArrayRef", [
            Node("exprSection", [wrapInt(q[1])])
        ], q[0])

"""
Partial evaluation, unrolling all loops and perform all integer computations.
After partial evaluation all qubit arguments should be constants.
"""

class PartialEvaluation(object):
    sym_table: T.Dict[str, int]
    current_pos: T.Optional[int]
    polytope_vars: T.List[str]
    measured_qubits: T.Set[str]
    emitted_insns: T.List[Node]
    def __init__(self, addgate = {},  paramdic = {}, target = 'isq', args = None, module = 'ir'):
        self.measured_qubits=set()
        self.polytope_vars=[]
        self.sym_table={}
        self.current_pos=None
        self.emitted_insns=[]
        self.out = []

        self.module = module
        self.target = target

        self.gateDic = addgate
        self.param = paramdic
        
        self.args = args
        if not args: self.args = {}

        self.gateDef = {}
        self.varDic = {}
        self.qDic = {}
        self.q_cnt = 0
        self.cDic = {}
        self.c_cnt = 0
        self.m_cnt = 0
        self.var_type = 'qbit'
        self.localVarDic = {}
        self.proc_key = ''

        self.for_cnt = 0
        self.for_val = []
        self.for_key = {}
        self.lamb = {}
        self.grad = False

        self.gateset = set(['H','X','Y','Z','S','T','CZ','CY', 'CX','CNOT', 'M', 'RX', 'RY', 'RZ', 'SD', 'TD', 'X2M', 'X2P', 'Y2M', 'Y2P'])
        self.openqasm_gate = {
            'H': 'h',
            'X': 'x',
            'Y': 'y',
            'Z': 'z',
            'X2P': 'rx(pi/2)',
            'X2M': 'rx(-pi/2)',
            'Y2P': 'ry(pi/2)',
            'Y2M': 'ry(-pi/2)',
            'S': 's',
            'T': 't',
            'SD': 'sdg',
            'TD': 'tdg',
            'CX': 'cx',
            'CNOT': 'cx',
            'CZ': 'cz',
            'CY': 'cy',
            'M': 'measure',
            'RX': 'rx',
            'RY': 'ry',
            'RZ': 'rz'
        }
        self.indextime = 0.0
        self.out_pos = 0
  

    def visitProgram(self, s: Node)->Node:
        #print(self.varDic)
        new_prog = []
        if s.leaf != None:
            for p in s.leaf:
                self.visitGateDef(p)

        self.gateDic.update(self.gateDef)
        #print("global gate: ", self.gateDic)

        for var in s.children[0].children:
            self.visitVarDef(var)
        
        #print("var dic: ", self.varDic)
        self.construct_globalVar()

        self.proc_key = 'main'
        self.localVarDic['main'] = {}

        self.visitProgBlock(s.children[1])
        new_prog = self.emitted_insns
        
        if self.module == 'ast':
            return Node("topNode", [s.children[0], Node("procBlock", new_prog, "main")])

        res = "\n".join(self.out)

        if self.target == 'openqasm':
            head = []
            head.append('OPENQASM 2.0;')
            head.append('include "qelib1.inc";')
            head.append(f'qreg q[{self.q_cnt}];')
            if self.m_cnt > 0:
                head.append(f'creg c[{self.m_cnt}];')
            head.append(res)
            res = '\n'.join(head)
        return res            
        
    def error_pos(self)->str:
        s = "line "+str(self.current_pos)
        if self.polytope_vars!=[]:
            s+=" (iteration ["
            f = lambda v: "{}={}".format(v, self.sym_table[v])
            s+=f(self.polytope_vars[0])
            for i in range(1, len(self.polytope_vars)):
                s+=", "
                s+=f(self.polytope_vars[i])
            s+="])"
        return s
    def qubit_array_size(self, name: str)->int:
        tmpDic = self.varDic
        localparas = self.localVarDic.get(self.proc_key)

        if localparas != None and name in localparas:
            tmpDic = localparas
        ty = tmpDic.get(name)
        if ty != None and (isinstance(ty, list) or isinstance(ty, tuple)):
            return T.cast(int, ty[1])
        return 0

    def emit(self, s: Node):
        self.emitted_insns.append(s)

    def visitUnitStat(self, s: Node):
        assert s.type=="unitStat"
        self.current_pos=s.pos
            
        if s.val == None:
            #judge gate and qbit number
            gateL = T.cast(T.Tuple[list], s.leaf)
            gate = gateL[0]
            gateq_cnt = 0
            if gate in self.gateset:
                if gate in ['H','X','Y','Z','S','T', 'RX', 'RY', 'RZ', 'SD', 'TD', 'X2M', 'X2P', 'Y2M', 'Y2P']:
                    if gate in ['RX', 'RY', 'RZ']:
                        self.grad = False
                        tmps = self.evaluateIntExpr(gateL[1], 1)
                        if self.grad: gateL[1] = (gateL[1], self.grad)
                        else: gateL[1] = (tmps, self.grad)
                    gateq_cnt = 1
                    if len(s.children.children) != 1:
                        ErrorThrow('in line {}, gate size does not coincide with the qubit number'.format(s.pos))
                else:
                    gateq_cnt = 2
                    if len(s.children.children) != 2:
                        ErrorThrow('in line {}, gate size does not coincide with the qubit number'.format(s.pos))
            else:
                gateInfo = self.gateDic.get(gate)
                if gateInfo == None:
                    ErrorThrow('in line {}, gate not defined'.format(s.pos))
                if gateInfo[0] != len(s.children.children):
                    ErrorThrow('in line {}, gate size does not coincide with the qubit number'.format(s.pos))
                gateq_cnt = gateInfo[0]

            operands = list(map(lambda x: self.evaluateAndCheckQubitRef(x), s.children.children))
            s.val = (gateL, operands)
        
        self.print(s.val, s.pos)

    def visitForeach(self, s: Node):
        assert s.type=="foreachStat"
        self.current_pos=s.pos

        var_name = T.cast(str, s.leaf)

        if(self.queryVariable(var_name)!=None):
            ErrorThrow('in line {}: the classical variable \'{}\' has been defined'.format(s.pos, var_name));
        
        if s.val == None:
            s.val = self.evaluateRangeAndSection(s.children[0], True)
        
        key = var_name + '_' + s.val
        if key not in self.lamb:
            self.lamb[key] = eval("lambda {}:{}".format("args", s.val), self.param)
            #self.lamb[key] = eval("f'"+s.val+"'", {'args': self.for_val})
        v_list = []
        try:
            v_list = self.lamb[key](self.for_val)
            #v_list = eval(self.lamb[key], self.param)
        except Exception as e:
            ErrorThrow('in line {}, expression calc error: {}'.format(s.pos, str(e)))

        self.localVarDic[self.proc_key][var_name] = "int"
        
        self.sym_table[var_name] = 0
        self.polytope_vars.append(var_name)
        self.for_key[var_name] = self.for_cnt
        self.for_val.append(0)
        self.for_cnt += 1

        for v in v_list:
            self.for_val[self.for_cnt-1] = v
            self.sym_table[var_name]=v
            self.visitProgBlock(s.children[1])

        self.for_val.pop(-1)
        self.for_key.pop(var_name)
        self.for_cnt -= 1
        del self.sym_table[var_name]
        self.polytope_vars.pop()

        del self.localVarDic[self.proc_key][var_name]
        pass

    def visitIfSate(self, s:Node):
        assert s.type=="ifStat"
        
        self.current_pos = s.pos
        if s.val == None:
            val1 = self.evaluateIntExpr(s.children[0], 1)
            val2 = self.evaluateIntExpr(s.children[1], 1)
            s.val = "{} {} {}".format(val1, s.children[2], val2)
        
        if s.val not in self.lamb:
            self.lamb[s.val] = eval("lambda {}:{}".format("args", s.val), self.param)
            #self.lamb[s.val] = eval("f'"+s.val+"'", {'args': self.for_val})
        cond = True
        try:
            cond = self.lamb[s.val](self.for_val)
            #cond = eval(self.lamb[s.val], self.param)
        except Exception as e:
            ErrorThrow('in line {}, expression calc error: {}'.format(s.pos, str(e)))
        
        if (cond):
            self.visitProgBlock(s.leaf[0])
        else:
            if len(s.leaf) == 2:
                self.visitProgBlock(s.leaf[1])
        

        

    def visitProgBlock(self, s:Node):
        assert s.type=="progBlock"
        stmt: Node
        for stmt in s.children:
            if stmt.type=="unitStat":
                self.visitUnitStat(stmt)
            elif stmt.type=="mStat":
                self.visitMeasurement(stmt)
            elif stmt.type=="foreachStat":
                self.visitForeach(stmt)
            elif stmt.type=="ifStat":
                self.visitIfSate(stmt)
            else:
                ICE("unknown statement type "+stmt.type)

    def visitMeasurement(self, s: Node):
        assert s.type=="mStat"
        self.current_pos=s.pos

        if s.val == None:
            arg = self.evaluateAndCheckQubitRef(s.children[0])
            s.val = ('M', [arg])
        #print(s.val)
        self.print(s.val, s.pos)

    def evaluateAndCheckQubitRef(self, s: Node)->T.List[QubitRef]:
        if s.type=="qubitSingleRef":
            qbit_name = s.leaf
            qbit_ty = self.queryVariable(qbit_name)
            if(qbit_ty==None):
                ThrowUndefinedVariable(s.pos, qbit_name)
            if(not is_qbit(qbit_ty)):
                ThrowTypeMismatch(s.pos, "qbit", stringify_type(qbit_ty))
            return (T.cast(str, s.leaf), 0, self.qDic.get(s.leaf))
        elif s.type=="qubitArrayRef":
            arr_name=s.leaf
            arr_ty = self.queryVariable(arr_name)
            if(arr_ty==None):
                ThrowUndefinedVariable(s.pos, arr_name)
            if(not is_array(arr_ty, "qbit")):
                ThrowTypeMismatch(s.pos, "qbit[]", stringify_type(arr_ty))
            size = self.qubit_array_size(T.cast(str, s.leaf))
            indices = self.evaluateRangeAndSection(s.children[0])
            '''
            for index in indices:
                if index >= size:
                    ThrowArrayOutOfBound(self.error_pos(), index, T.cast(str, s.leaf), size)
            '''
            return (T.cast(str, s.leaf), size, self.qDic.get(s.leaf), indices)#list(map(lambda x: (T.cast(str, s.leaf), x), indices))
        else:
            ICE("Unknown qubitref type: "+s.type)
    def evaluateRangeAndSection(self, s: Node, looprange: bool = False)->T.Iterable[int]:
        
        if s.type=="exprRange":
            a=None
            b=None
            c=None
            if s.children[0]!=None:
                a=self.evaluateIntExpr(s.children[0])
            if s.children[1]!=None:
                b=self.evaluateIntExpr(s.children[1])
            if s.children[2]!=None:
                c=self.evaluateIntExpr(s.children[2])
            
            assert a!=None
            assert b!=None
            if c==None:
                c="1"
            return "range({},{},{})".format(a, b, c)
            
            #if looprange:
            #    return range(a,b,c)
            
        elif s.type=="exprSection":
            res = '['
            for x in s.children:
                res += self.evaluateIntExpr(x)
                res += ','
            res = res[:-1]+']'
            return res#list(map(lambda x: self.evaluateIntExpr(x), s.children))
        else:
            ICE("Unknown range/section type: "+s.type)
            
    def evaluateIntExpr(self, s: Node, allow_type = 0)->int:

        need_type = (int)
        if allow_type == 1:
            need_type = (int, float)

        if s.type=="intExprVar":
            var_name=s.leaf
            if var_name == 'pi': return str(np.pi)
            var_ty = self.queryVariable(var_name)
            if(var_ty==None):
                val = self.queryParam(var_name, s.pos)
                if val == None:
                    ThrowUndefinedVariable(s.pos,var_name)
                else:
                    if val in self.args: self.grad = True
                    return str(val)
            if(not is_int(var_ty)):
                ThrowTypeMismatch(s.pos, "int", stringify_type(var_ty))
            return f"args[{self.for_key[var_name]}]"
        
        elif s.type=="intExprArrayRef":
            var_name = s.leaf
            idx = self.evaluateIntExpr(s.children[0], 0)

            val = self.queryParam(var_name, s.pos, idx)
            if val == None:
                ThrowUndefinedVariable(s.pos,var_name)
            else:
                if val in self.args: self.grad = True
                return "{}[{}]".format(val, idx)

        elif s.type=="intExprLiteral":
            if not isinstance(s.leaf, need_type):
                ThrowTypeMismatch(s.pos, str(need_type), type(s.leaf))
            return str(s.leaf)

        elif s.type=="intExprBinary":
            lhs: Node = s.children[0]
            rhs: Node = s.children[1]
            l = self.evaluateIntExpr(lhs, allow_type)
            r = self.evaluateIntExpr(rhs, allow_type)
            if s.leaf=="+":
                return "({}+{})".format(l,r)
            elif s.leaf=="-":
                return "({}-{})".format(l,r)
            elif s.leaf=="*":
                return "({}*{})".format(l,r)
            elif s.leaf=="/":
                if r==0:
                    ThrowDivisionByZero(self.error_pos())
                if allow_type == 0:
                    return "({}//{})".format(l,r)
                else:
                    return "({}/{})".format(l,r)
            elif s.leaf=="%":
                if r==0:
                    ThrowDivisionByZero(self.error_pos())
                return "({}%{})".format(l,r)
            else:
                ICE("Unknown op type: "+str(s.leaf))
        else:
            ICE("Unknown intexpr type: "+s.type)


    def evaluateTheta(self, s: Node):

        need_type = (int, float)

        if s.type=="intExprVar":
            var_name=s.leaf
            if var_name == 'pi': return str(np.pi)
            var_ty = self.queryVariable(var_name)
            if(var_ty==None):
                val = self.queryParam(var_name, s.pos)
                if val == None:
                    ThrowUndefinedVariable(s.pos,var_name)
                else:
                    if val in self.args: return str(val)
                    else: return self.param[val]

            if(not is_int(var_ty)):
                ThrowTypeMismatch(s.pos, "int", stringify_type(var_ty))
            
            return self.for_val[self.for_key[var_name]]
        
        elif s.type=="intExprArrayRef":
            
            var_name = s.leaf
            idx = self.evaluateTheta(s.children[0])
            if not isinstance(idx, int):
                ThrowTypeMismatch(s.pos, "int", stringify_type(idx))
            val = self.queryParam(var_name, s.pos, idx)
            if val == None:
                ThrowUndefinedVariable(s.pos,var_name)
            else:
                if val in self.args: return f"{val}[{idx}]"
                return self.param[val][idx]

        elif s.type=="intExprLiteral":
            if not isinstance(s.leaf, need_type):
                ThrowTypeMismatch(s.pos, str(need_type), type(s.leaf))
            return s.leaf

        elif s.type=="intExprBinary":
            lhs: Node = s.children[0]
            rhs: Node = s.children[1]
            l = self.evaluateTheta(lhs)
            r = self.evaluateTheta(rhs)
            if isinstance(l, str) or isinstance(r, str):
                if s.leaf=="+":
                    return "({}+{})".format(l,r)
                elif s.leaf=="-":
                    return "({}-{})".format(l,r)
                elif s.leaf=="*":
                    return "({}*{})".format(l,r)
                elif s.leaf=="/":
                    if r==0:
                        ThrowDivisionByZero(self.error_pos())
                    return "({}/{})".format(l,r)
                elif s.leaf=="%":
                    if r==0:
                        ThrowDivisionByZero(self.error_pos())
                    return "({}%{})".format(l,r)
                else:
                    ICE("Unknown op type: "+str(s.leaf))
            else:
                if s.leaf=="+":
                    return l+r
                elif s.leaf=="-":
                    return l-r
                elif s.leaf=="*":
                    return l*r
                elif s.leaf=="/":
                    if r==0:
                        ThrowDivisionByZero(self.error_pos())
                    return l / r
                elif s.leaf=="%":
                    if r==0:
                        ThrowDivisionByZero(self.error_pos())
                    return l % r
                else:
                    ICE("Unknown op type: "+str(s.leaf))
        else:
            ICE("Unknown intexpr type: "+s.type)


    def visitGateDef(self, s:Node):
        p = s.children
        matrixC = p[1]
        l = matrixC.split(';')
        #print(l)
        rowS = len(l)
        #print(rowS)

        current_ID = p[0]

        if self.varDic.get(p[0]) != None:
            ErrorThrow('in line ' + str(s.pos) + ', '+ p[2] + "redeclaration!")
        else:
            self.varDic[p[0]] = ('gate',False)

        power2list = [2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536]
        if not (rowS in power2list):
            ErrorThrow('in line '+str(s.pos)+', gate definition of ' + str(current_ID) + \
                                    ': the dimension of matrix is not a power of 2.')

        rowList = []
        for i in range(rowS):
            try:
                st = l[i].replace('i','j').replace(' ','')
                st = st.replace(',j','1j').replace('+j','+1j').replace('-j','-1j')
                scope = {}
                exec('a = np.array([' + st + '])',None,scope)
                b = len(scope['a'])
                if b != rowS:
                    ErrorThrow('in line '+str(s.pos)+', gate definition of ' + str(current_ID) + \
                                    ': matrix not square.')
                    #print(rowS,b)
                rowList.append(scope['a'])
            except Exception as e:
                print(e)
                sys.exit(0)
            finally:
                pass

        flag, res = decompose(rowList, rowS, current_ID, s.pos)

        if not flag:
            ErrorThrow(res)
        
        self.gateDef[p[0]] = res
        
    def visitVarDef(self, s:Node):
        for p in s.children: 
            if (len(p) == 1):
                if (self.proc_key != ''):
                    if (self.localVarDic[self.proc_key].get(p[0]) != None):
                        ErrorThrow('in line ' + str(s.pos) + ', '+ p[0] + "redeclaration!")
                    self.localVarDic[self.proc_key][p[0]] = self.var_type
                else:
                    if (self.varDic.get(p[0]) != None):
                        ErrorThrow('in line ' + str(s.pos) + ', '+ p[0] + "redeclaration!")
                    self.varDic[p[0]] = self.var_type
            else:
                p1: VarKey = p[0]
                p3: int = p[1]
                if type(p[1]) != int:
                    ErrorThrow('in line ' + str(s.pos) + ', '+ p[1] + "is not an integer!")
                if (self.proc_key != ''):
                    if (self.localVarDic[self.proc_key].get(p[0]) != None):
                        ErrorThrow('in line ' + str(s.pos) + ', '+ p[0] + "redeclaration!")
                    self.localVarDic[self.proc_key][p1] = (self.var_type,p3)
                else:
                    if (self.varDic.get(p[0]) != None):
                        ErrorThrow('in line ' + str(p.pos) + ', '+ p[0] + " redeclaration!")
                    self.varDic[p1] = (self.var_type, p3)
    
    def construct_globalVar(self):
        
        self.qDic = {}
        self.cDic = {}
        self.q_cnt = 0
        self.c_cnt = 0
        for key in self.varDic:
            if (self.varDic[key] == 'qbit'):
                self.qDic[key] = self.q_cnt
                self.q_cnt = self.q_cnt + 1
            elif (self.varDic[key] == 'int'):
                self.cDic[key] = self.c_cnt
                self.c_cnt = self.c_cnt + 1
            elif self.varDic[key][0] == 'int':
                self.cDic[key] = self.c_cnt
                tt = T.cast(int, self.varDic[key][1])
                self.c_cnt = self.c_cnt + tt
            elif self.varDic[key][0] == 'qbit':
                self.qDic[key] = self.q_cnt
                tt = T.cast(int, self.varDic[key][1])
                self.q_cnt = self.q_cnt + tt
    
    def queryVariable(self, name: VarKey)-> T.Optional[VarType]:
        localparas = self.localVarDic.get(self.proc_key)
        if(localparas!=None and name in localparas):
            return localparas[name]
        else:
            return self.varDic.get(name)
    
    def queryParam(self, name, pos, idx = -1):

        if name not in self.param:
            return None
        
        return name
        '''
        val = 0
        if idx == -1:
            if not isinstance(self.param[name], (int, float, complex)):
                ThrowTypeMismatch(pos, "int/float/complex", type(self.param[name]))
            val = self.param[name]
        else:
            if not isinstance(self.param[name], list):
                ThrowTypeMismatch(pos, "list", type(self.param[name]))
            if idx >= len(self.param[name]):
                ThrowArrayOutOfBound(pos, idx, name, len(self.param[name]))
            val = self.param[name][idx]

        return val
        '''
    
    def no_indent_out_append(self, st):
        #t = time.time()
        self.out.append(st)
        #self.indextime += time.time() - t
            
    def get_qcis_reg(self, q:QubitRef):
        qid = ''
        offset = 0
        if isinstance(q, str):
            qid = q
        else:
            qid = q[0]
            offset = q[1]
        index = self.qDic.get(qid)
        if(index==None):
            ICE("bad variable")
        index += offset
        return "Q{:0>2d}".format(index+1)

    def get_qop(self, gate, qbit, param):
        
        if self.target == 'openqasm':
            s = self.openqasm_gate[gate]
            if gate == 'M':
                s += f' q[{int(qbit[0])-1}] -> c[{self.m_cnt}]'
                self.m_cnt += 1
            else:
                if gate in ['RX', 'RY', 'RZ']:
                    s += f'({param[0]})'
                
                if gate in ['CNOT', 'CX', 'CY', 'CZ']:
                    s += f' q[{int(qbit[0])-1}], q[{int(qbit[1])-1}]'
                else:
                    s += f' q[{int(qbit[0])-1}]'
            return s+';'
        else:
            s = gate
            if gate in ['CNOT', 'CX', 'CY', 'CZ']:
                s = f"{gate} Q{qbit[0]} Q{qbit[1]}"
            else:    
                for q in qbit:
                    s += f' Q{q}'
                if param:
                    s += f' {param[0]}'
            return s

    def print(self, val, pos):

        gate = val[0][0]
        theta = 0.0
        if len(val[0]) == 2:
            t, f = val[0][1]
            try:
                if f:
                    theta = self.evaluateTheta(t)
                else:
                    if t not in self.lamb:
                        self.lamb[t] = eval("lambda {}:{}".format("args", t), self.param)
                        #self.lamb[val[0][1]] = eval("f'"+val[0][1]+"'", {'args': self.for_val})
                    theta = self.lamb[t](self.for_val)
                    #theta = eval(self.lamb[val[0][1]], self.param)
                    theta %= 4*np.pi
                    if theta > 2*np.pi: theta -= 4*np.pi
                    # theta /= 2
                    # theta= round(theta,4)
            except Exception as e:
                ErrorThrow('in line {}, expression calc error: {}'.format(pos, str(e)))

        qlist = []
        try:
            for q in val[1]:
                if q[1] == 0:
                    qlist.append([0])
                else:  
                    if q not in self.lamb:
                        self.lamb[q] = eval("lambda {}:{}".format("args", q[3]), self.param)
                        #self.lamb[q] = eval("f'"+q[3]+"'", {'args': self.for_val})
                    qlist.append(self.lamb[q](self.for_val))
                    #qlist.append(eval(self.lamb[q], self.param))
        except Exception as e:
            ErrorThrow('in line {}, expression calc error: {}'.format(pos, str(e)))

        if not all(len(qlist[0])==len(x) for x in qlist):
            ThrowBulkSizeMismatch(self.error_pos(), qlist)
        
        gateq_cnt = len(qlist)
        for i in range(len(qlist[0])):
            qbit = []
            for id in range(gateq_cnt):

                offset=qlist[id][i]
                if not isinstance(offset, int):
                    ErrorThrow('in line {}, index need int'.format(pos))
                qid = "{}".format(val[1][id][2]+offset+1)    
                
                if val[1][id][1] > 0 and offset >= val[1][id][1]:
                    ThrowArrayOutOfBound(self.error_pos(), offset, val[1][id][0], val[1][id][1])

                if qid in self.measured_qubits:
                    if val[1][id][1] == 0:
                        ThrowAlreadyMeasured(self.error_pos(), val[1][id][0])
                    else:
                        ThrowAlreadyMeasured(self.error_pos(), val[1][id][0], offset)    
                qbit.append(qid)

            if(len(set(qbit))!=len(qbit)):
                ThrowDuplicateQubit(self.error_pos())

            if gate in self.gateset:
                s = gate
                param = []
                if gate in ['RX', 'RY', 'RZ']:
                    param.append(theta)

                self.no_indent_out_append(self.get_qop(s, qbit, param))
                if gate == 'M':
                    self.measured_qubits.add(qbit[0])
            else:
                gateInfo = self.gateDic.get(gate)
                for g in gateInfo[1]:
                    s = g[0]
                    param = []
                    if g[0] in ['CNOT', 'CX', 'CY', 'CZ']:
                        l,r = T.cast(T.Tuple[int, int], g[2])
                        qbit_g = [qbit[l], qbit[r]]
                    else:
                        l = T.cast(int, g[2])
                        qbit_g = [qbit[l]]
                        if g[0] in ['RX', 'RY', 'RZ']:
                            param = [str(g[1])]
                    self.no_indent_out_append(self.get_qop(s, qbit_g, param))
            