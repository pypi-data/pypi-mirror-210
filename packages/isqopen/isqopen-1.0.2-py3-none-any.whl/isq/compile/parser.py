from ply import (
    lex,
    yacc
)
import typing as T
from typing import (cast, List, Any)
from .qtypes import *
from . import tokrules
from .tokrules import tokens
from isq.globalVar import msgDic
import numpy as np
import sys
import logging
from isq.config import debug_mode
from isq.errors import *
from .passes import PartialEvaluation
import time


current_line = 0
current_ID = ''

class IR:
    def __init__(self):
        self.out = ""
        self.error: Any = None

def trace_time(timer, reason: str):
    t = time.time()
    if debug_mode:
        print("Time cost for {}: {}s".format(reason, t-timer))
    return t

# 顶层文法

def p_program(p):
    '''program : varDef procedureBody
               | gateDef varDef procedureBody'''
    #'''program : programDef programBody'''
    
    if debug_mode == True:
        print("in program")
    if (len(p) == 3):
        p[0] = Node("topNode",[p[1],p[2]])
    else:
        p[0] = Node("topNode",[p[2],p[3]], p[1])


def p_gateDef(p):
    '''gateDef : gateDefclause
               | gateDefclause gateDef'''
    if (len(p) == 2):
        p[0] = [Node('gateDef', p[1], None, p.lineno(0))]
    else:
        p[0] = [Node('gateDef', p[1], None, p.lineno(0))] + p[2]

def p_gDefID(p):
    '''gDefID : ID '''
    '''gDefID : ID '''
    global current_ID
    current_ID = p[1]
    p[0] = p[1]
"""

"""
def p_gateDefclause(p):
    '''gateDefclause : DEFGATE gDefID '=' '[' matrixContents ']' ';' '''
    p[0] = [p[2], p[5]]
    #print('now defining a gate')

def p_matrixContents(p):
    ''' matrixContents : CNUMBER
                       | CNUMBER ',' matrixContents
                       | CNUMBER ';' matrixContents'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2] + p[3]

def p_CNUMBER(p):
    ''' CNUMBER : NumberExpr
                | '-' NumberExpr'''
    if len(p) == 2:
        p[0] = str(p[1])
    else:
        p[0] = "".join(p[1:len(p)])

def p_NumberExpr(p):
    ''' NumberExpr : NUMBER
                   | NUMBER '+' NUMBER
                   | NUMBER '-' NUMBER '''
    p[0] = "".join([str(it) for it in p[1:len(p)]])

# to do

def p_varDef(p):
    '''varDef : defclause
              | varDef defclause'''
    if (len(p) == 2):
        p[0] = Node("defBlock",[p[1]])
    else:
        p[0] = Node("defBlock",p[1].children+[p[2]])

def p_defclause(p):
    ''' defclause : QBIT seen_Qbit id_list ';' '''
    global current_line
    if debug_mode == True:
        print("qbit defining")
    p[0] = Node("qbitDef", p[3], None, p.lineno(0))

def p_seen_Qbit(p):
    '''seen_Qbit : '''

#def p_seen_Int(p):
#    '''seen_Int : '''
    
def p_id_list(p):
    '''id_list : ID
               | id_list ',' ID
               | ID '[' NUMBER ']'
               | id_list ',' ID '[' NUMBER ']' '''
    
    global current_line
    
    if (len(p) == 2):
        p[0] = [[p[1]]]
    elif len(p) == 4:
        p[0] = p[1] + [[p[3]]]
    elif len(p) == 5:
        p[0] = [[p[1], p[3]]]
    else:
        p[0] = p[1] + [[p[3], p[5]]]


#def p_seen_Main(p):
#    '''seen_Main : '''
#
#def p_procedureMain(p):
#    ''' procedureMain :  PROCEDURE seen_Main MAIN '(' ')' '{' '}'
#                        | PROCEDURE seen_Main MAIN '(' ')' '{' procedureBody '}' '''
#                        #| PROCEDURE MAIN '(' ')' '{' localVarDef ';' programBlock '}' '''
#
#    st = str(p[3])
#
#    current_line = p.lineno(1)
#    if (p.lineno(1) != p.lineno(5)):
#        ErrorThrow('in line ' + str(p.lineno(1)))
#
#    if (len(p) == 8):
#        p[0] = Node('procBlock',[],'main')
#    elif (len(p) == 9):
#        p[0] = Node('procBlock',[p[7]],'main')
#    else:
#        p[0] = Node('procBlock',[p[7],p[9]],'main')

def p_procedureBody(p):
    ''' procedureBody : programBlock
                        | PROCEDURE MAIN '(' ')' '{' programBlock '}' '''
                    #| varDef programBlock

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[6]
def p_statement(p):
    ''' programStatement : qbitUnitaryStatement
                     | measureStatement
                     | foreachStatement
                     | ifStatement '''
    p[0]=p[1]
def p_programBlock(p):
    ''' programBlock : programStatement
                     | programBlock programStatement '''
    if (len(p) == 2):
        p[0] = Node('progBlock',[p[1]],None)
    else:
        p[0] = Node('progBlock',p[1].children + [p[2]],None)
        #if debug_mode == True:
            #print(p[1].type,p[2].type)


class Arg_RangeExpr1(LexResult, Tuple[Node, Node, Any, Node]):
    ...
class Arg_RangeExpr2(LexResult, Tuple[Node, Node, Any, Node, Any, Node]):
    ...
def p_rangeExpr(p: Union[Arg_RangeExpr1, Arg_RangeExpr2]):
    ''' rangeExpr : optionalIntExpr ':' optionalIntExpr
                  | optionalIntExpr ':' optionalIntExpr ':' optionalIntExpr '''
    if(len(p)==4):
        p[0]=Node('exprRange',[p[1], p[3], None], None, p.lineno(1))
    else:
        p[0]=Node('exprRange',[p[1], p[3], p[5]], None, p.lineno(1))

def p_optionalIntExpr(p):
    ''' optionalIntExpr : intExpr
                       | emptyStatement'''
    if(p[1]=="empty"):
        p[0]=None
    else:
        p[0]=p[1]
class Arg_SectionExpr1(LexResult, Tuple[Node, Node]):
    ...
class Arg_SectionExpr2(LexResult, Tuple[Node, Node, Literal[","], Node]):
    ...
def p_section(p: T.Union[Arg_SectionExpr1, Arg_SectionExpr2]):
    '''sectionExpr : intExpr
                | sectionExpr ',' intExpr '''
    if(len(p)==2):
        p1=T.cast(Arg_SectionExpr1, p)
        p1[0]=Node("exprSection", [p1[1]], None)
    else:
        p2=T.cast(Arg_SectionExpr2, p)
        p2[0]=Node("exprSection", p2[1].children+[p2[3]], None)
class Arg_QubitExpr1(LexResult, Tuple[Node, VarKey]):
    ...
class Arg_QubitExpr2(LexResult, Tuple[Node, VarKey, Literal["["], Node, Literal["]"]]):
    ...
def p_qubitExpr(p: Union[Arg_QubitExpr1, Arg_QubitExpr2]):
    '''qubitExpr : ID 
                 | ID '[' sectionExpr ']'
                 | ID '[' rangeExpr ']' '''
    if(len(p)==2):
        p1 = T.cast(Arg_QubitExpr1, p)
        p1[0]=Node("qubitSingleRef", [], p1[1], p.lineno(1))
    else:
        p2 = T.cast(Arg_QubitExpr2, p)
        p2[0]=Node("qubitArrayRef", [p2[3]], p2[1], p.lineno(1))
class Arg_QubitListExpr1(LexResult, Tuple[Node, Node]):
    ...
class Arg_QubitListExpr2(LexResult, Tuple[Node, Node, Literal[","], Node, Literal["]"]]):
    ...
def p_qubitListExpr(p: Union[Arg_QubitListExpr1, Arg_QubitListExpr2]):
    '''qubitListExpr : qubitExpr
                     | qubitListExpr ',' qubitExpr '''
    if(len(p)==2):
        p1=T.cast(Arg_QubitListExpr1, p)
        p1[0]=Node("exprQubitList", [p1[1]], None)
    else:
        p2=T.cast(Arg_QubitListExpr2, p)
        p2[0]=Node("exprQubitList", p2[1].children+[p2[3]], None)
class Arg_IntExprAtom1(LexResult, Tuple[Node, VarKey]):
    ...
class Arg_IntExprAtom2(LexResult, Tuple[Node, int]):
    ...
class Arg_IntExprAtom3(LexResult, Tuple[Node, VarKey, Any, Node, Any]):
    ...
class Arg_IntExprAtom4(LexResult, Tuple[Node, Any, Node, Any]):
    ...
class Arg_IntExprAtom5(LexResult, Tuple[Node, Literal["M"], Literal["<"],  Node,  Literal[">"]]):
    ...

def p_intExprAtom(p: Union[Arg_IntExprAtom1, Arg_IntExprAtom2, Arg_IntExprAtom3, Arg_IntExprAtom4, Arg_IntExprAtom5]):
    ''' intExprAtom : ID 
                    | NUMBER 
                    | ID '[' intExpr ']'
                    | '(' intExpr ')'  '''
    #               | M '<' qubitExpr '>' 
    if(len(p)==2):
        if(isinstance(p[1], str)):
            # variable
            p1=T.cast(Arg_IntExprAtom1, p)
            p1[0]=Node("intExprVar", None, p1[1], p.lineno(1))
        else:
            # integer literal
            p2=T.cast(Arg_IntExprAtom2, p)
            p2[0]=Node("intExprLiteral", None, p2[1], p.lineno(1))
    elif(len(p)==5 and p[2]=="["):
        # array access
        p3=T.cast(Arg_IntExprAtom3, p)
        '''
        arr_name=p3[1]
        arr_ty = queryVariable(p3[1])
        if(arr_ty==None):
            ThrowUndefinedVariable(p.lineno(1), arr_name)
        if(not is_array(arr_ty)):
            ThrowTypeMismatch(p.lineno(1), "int[]", stringify_type(arr_ty))
        arr_ty2 = T.cast(ArrayType, arr_ty)
        if(not is_int(arr_ty2)):
            ThrowTypeMismatch(p.lineno(1), "int[]", stringify_type(arr_ty))
        '''
        p3[0]=Node("intExprArrayRef", [p3[3]], p3[1])
    elif(len(p)==4):
        # bracket
        p4=T.cast(Arg_IntExprAtom4, p)
        p4[0]=p4[2]
    elif(len(p)==8):
        # measurement
        p5=T.cast(Arg_IntExprAtom5, p)
        p5[0]=Node("intExprMeasurement", [p5[3]], p.lineno(1))
    else:
        ICE()
class Arg_IntExprBinary(LexResult, Tuple[Node, Node, str, Node]):
    ...
class Arg_IntExprSingle(LexResult, Tuple[Node, Node]):
    ...
def p_intTier1Expr(p: Union[Arg_IntExprBinary, Arg_IntExprSingle]):
    """ intExprTier1 : intExprAtom 
                     | intExprTier1 '*' intExprAtom 
                     | intExprTier1 '/' intExprAtom
                     | intExprTier1 '%' intExprAtom """
    if(len(p)==2):
        p1=T.cast(Arg_IntExprSingle, p)
        p1[0]=p1[1]
    else:
        p2=T.cast(Arg_IntExprBinary, p)
        p2[0]=Node("intExprBinary", [p2[1], p2[3]], p2[2])
def p_intTier2Expr(p: Union[Arg_IntExprBinary, Arg_IntExprSingle]):
    """ intExprTier2 : intExprTier1 
                     | intExprTier2 '+' intExprTier1 
                     | intExprTier2 '-' intExprTier1 
                     | """
    if(len(p)==2):
        p1=T.cast(Arg_IntExprSingle, p)
        p1[0]=p1[1]
    else:
        p2=T.cast(Arg_IntExprBinary, p)
        p2[0]=Node("intExprBinary", [p2[1], p2[3]], p2[2])
def p_term(p:Arg_IntExprSingle):
    """ intExpr : intExprTier2
                | '-' intExprTier2 """
    if len(p) == 2:
        p[0]=p[1]
    else:
        p3=T.cast(Arg_IntExprBinary, p)
        c = Node("intExprLiteral", None, -1, p.lineno(2))
        p3[0] = Node("intExprBinary", [c, p[2]], '*')
    
    
class Arg_Foreach(LexResult, Tuple[Node, Any, VarKey, Any, Node, Any, Node, Any]):
    ...
def p_foreachStatement(p: Arg_Foreach):
    '''foreachStatement : FOR ID IN rangeExpr '{' programBlock '}' '''
    if(p[4].children[0]==None or p[4].children[1]==None):
        ThrowLoopRangeUnknown(p.lineno(1))
    p[0]=Node('foreachStat',[p[4], p[6]],p[2], p.lineno(2))


def p_asso(p):
    ''' asso : EQ
            | GE
            | LE
            | NE
            | '<'
            | '>'
    '''
    p[0] = p[1]

def p_ifStatement(p):
    ''' ifStatement : IF '(' intExpr asso intExpr ')' '{' programBlock '}' 
                | IF '(' intExpr asso intExpr ')' '{' programBlock '}' ELSE '{' programBlock '}' '''
    if len(p) == 10:
        p[0] = Node('ifStat', [p[3], p[5], p[4]], [p[8]], p.lineno(1))
    else:
        p[0] = Node('ifStat', [p[3], p[5], p[4]], [p[8], p[12]], p.lineno(1))

def p_qbitUnitaryStatement(p):
    ''' qbitUnitaryStatement : uGate '<' qubitListExpr '>' ';' 
        | uGate '(' qubitListExpr  ')' ';' 
        | rGate '<' intExpr ',' qubitListExpr '>' ';'
        | rGate '(' intExpr ',' qubitListExpr ')' ';' '''
    #''' qbitUnitaryStatement : id_list '=' uGate '[' id_list ']' ';' '''
    if (p.lineno(1) != p.lineno(len(p)-1)):
        ErrorThrow('in line ' + str(p.lineno(1)))
    
    if len(p) == 6:
        p[0] = Node('unitStat',p[3], [p[1]], p.lineno(1))
    else:
        p[0] = Node('unitStat',p[5], [p[1], p[3]], p.lineno(1))
        
    # turn tuple (qID, index) to string 'qID[index]'
    #print(listU)
    
def p_rGate(p):
    ''' rGate : RX
              | RY
              | RZ '''
    p[0] = p[1]
    
def p_uGate(p):
    ''' uGate : H
              | X
              | Y
              | Z
              | S
              | T
              | SD
              | TD
              | X2P
              | X2M
              | Y2P
              | Y2M
              | CZ
              | CNOT
              | CX
              | CY
              | ID '''
    if debug_mode:
        print("uGate: ", p[1])
    p[0] = p[1]
    
def p_measureStatement(p):
    ''' measureStatement : M '<' qubitExpr '>' ';'
        | M '(' qubitExpr ')' ';' '''
    p[0] = Node('mStat',  [p[3]], None, p.lineno(3))


def p_emptyStatement(p):
    '''emptyStatement : '''
    p[0] = 'empty'


def p_error(p):
    if isinstance(p, lex.LexToken):
        raise CompileError(1001, "in line: {}, can not parser the sentence at token: '{}'".format(p.lineno, p.value))
    else:
        raise CompileError(1001, "lack ';' or '}' at the end of code")
    #ErrorThrow("Syntax error in line " + str(p.lineno))


'''
    defgate U_1 = [1.2,3.2,4.3,4.51,1,1,12,2,2,23,3,3,3]
    qbit x
    -x + 24 y + z >= 0 //this is a comment
    9 y - z + 72 x < -1
    y - z + x == 8
    for (i=1i<0i++)
    (x,y) = CX(x,y)
    
'''


def compile(ir: IR, data, target='isq', gate = {}, par = {}, args = None):

    pre_time = time.time()
    try:
        lexer = lex.lex(module = tokrules)
        lexer.input(data)
        pre_time = trace_time(pre_time, "lex")

        #parser = yacc.yacc(debug=True)
        parser = yacc.yacc(debug=True)
        lexer.lineno = 1

        #print("now starting parsing")

        s = T.cast(Node, parser.parse(data, tracking = True))
        pre_time = trace_time(pre_time, "yacc")
        # if debug_mode == True:
        # print(s.type)
        
        #s = passes.flatten_qbitdef_list(s)
        #globalVar.trace_time("flatten")
        mypass = PartialEvaluation(gate, par, target, args)
        ir.out = mypass.visitProgram(s)
        pre_time = trace_time(pre_time, "partial evaluation")
        #return 0
        #if globalVar.print_ast:
        #    print(json.dumps(s, default=vars, indent=4))
        #    return 0
        # construct symbol table for procedure calls
        #prev_traverse(s)
        #globalVar.trace_time("prev_traverse")

        #print(globalVar.callDic)
        #construct_globalVar()
        # output the IR
        #traverse(ir, s)
        #pre_time = trace_time(pre_time, "traverse")

        # file_o = open('output.txt','w')
        # file_o.write(globalVar.output)
        # file_o.close()
        
        #ir.out = Simplify.further_reduce_step2(ir.out)
        #pre_time = trace_time(pre_time, "reduce result")
        
        #if debug_mode == True:
        #    print("memory: ", get_size(mypass)+get_size(ir))

        if debug_mode == True:
            print("compilation succeed!")

        #if debug_mode == True:
        #   print("------------------------the compilation result------------------------")
        return 0

    except CompileError as e:
        ir.error = "{}: {}".format(msgDic[e.code], e.msg)
        return -1