from typing import (Literal, Tuple, Union, Protocol, Generic, TypeVar)
import typing as T
import types
from isq.errors import ICE
import inspect
import sys

ProcedureKey = str
GateKey = str
VarKey = str
QbitType = Literal["qbit"]
IntType = Literal["int"]
ProcType = Literal["proc"]
GateType = Tuple[Literal["gate"], bool]
ArrayType = Tuple["VarType", int]
VarType = Union[QbitType, IntType, ProcType, GateType, ArrayType]
RegisterId = int

DecomposedGate = Tuple[str, float, Union[int, Tuple[int, int]]]

def is_int(ty: VarType)->bool:
    return ty=="int"
def is_qbit(ty: VarType)->bool:
    return ty=="qbit"
def is_proc(ty: VarType)->bool:
    return ty=="proc"
def is_array(ty: VarType, elm: T.Optional[VarType] = None)->bool:
    if(not isinstance(ty, list) and not isinstance(ty, tuple)):
        return False
    if(not isinstance(ty[1], int)):
        return False
    if(elm!=None and ty[0]!=elm):
        return False
    return True
def is_gate(ty: VarType)->bool:
    if(not isinstance(ty, list) and not isinstance(ty, tuple)):
        return False
    return isinstance(ty[1], bool)

def stringify_type(ty: VarType)->str:
    if(is_int(ty)):
        return "int"
    elif is_qbit(ty):
        return "qbit"
    elif is_array(ty):
        ty_array=T.cast(ArrayType, ty)
        return "{}[{}]".format(stringify_type(ty_array[0]), ty_array[1])
    elif is_gate(ty):
        ty_gate=T.cast(GateType, ty)
        return "gate<{}>".format(ty_gate[1])
    elif is_proc(ty):
        return "proc"
    else:
        ICE("unrecognized type "+str(ty))
"""
Node type semantics:
type             children                                    leaf         Description
topNode          Tuple[defBlock, procBlock]                  None         TOP NODE.
defBlock         List[qbitDef]                               None         List of qubit definitions
qbitDef          Tuple[var_array]                            None         List of qubit definitions in one stmt.
var              Optional[Tuple[Union[var, var_array]]]      VarKey       Define one qubit.
var_array        Optional[Tuple[Union[var, var_array]]]      VarKey       Define one qubit. Use chaining to chain next definition.
procBlock        Union[Tuple[()], Tuple[progBlock]]          "main"       Define procedure, only main supported yet.
progBlock        List[statement]        
exprRange        Tuple[Optional[intExpr]*3]                  None         Define a range slice. Comfort to Python slice class.
exprSection      List[intExpr]                               None         Define a selection on multiple indices.
qubitSingleRef   Tuple[()]                                   VarKey       Reference to single qubit.
qubitArrayRef    Tuple[Union[exprRange, exprSection]]        VarKey       Reference to qubit array.
exprQubitList    List[Union[qubitSingleRef, qubitArrayRef]]  None         Unitary op argument list.
intExprVar       Tuple[()]                                   VarKey       Integer variable reference.
intExprLiteral   Tuple[()]                                   int          Integer literal.
intExprBinary    Tuple[intExpr, intExpr]                     '+-*/'       Binary integer op.
foreachStat      Tuple[exprRange, progBlock]                 VarKey       Define a variable and perform for-loop.
unitStat         Tuple[exprQubitList]                        [int, str]   Unitary gate op.
mStat            Tuple[Union[qubitSingleRef, qubitArrayRef]] None         Measure.
"""
class Node:
    def __init__(self,type: str,children: T.List[T.Any]=None,leaf: T.Any=None , pos=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]
        self.leaf = leaf
        self.pos=pos
        self.val = None

class LexResult(Protocol):
    def lineno(self, arg: int)->int:
        ...
    def __setitem__(self, key: Literal[0], value: Node):
        ...

def get_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if hasattr(obj, '__dict__'):
        for cls in obj.__class__.__mro__:
            if '__dict__' in cls.__dict__:
                d = cls.__dict__['__dict__']
                if inspect.isgetsetdescriptor(d) or inspect.ismemberdescriptor(d):
                    size += get_size(obj.__dict__, seen)
                break
    if isinstance(obj, dict):
        # 这里避免重复计算
        size += sum((get_size(v, seen) for v in obj.values() if not isinstance(v, (str, int, float, bytes, bytearray))))
        # size += sum((get_size(k, seen) for k in obj.keys())) 
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        # 这里避免重复计算
        size += sum((get_size(i, seen) for i in obj if not isinstance(i, (str, int, float, bytes, bytearray))))

    if hasattr(obj, '__slots__'): 
        size += sum(get_size(getattr(obj, s), seen) for s in obj.__slots__ if hasattr(obj, s))

    return size