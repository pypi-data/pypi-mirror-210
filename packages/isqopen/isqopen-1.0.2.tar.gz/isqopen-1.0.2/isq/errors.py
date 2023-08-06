from .config import debug_mode
import sys
import traceback
import typing as T
class SyntaxTypeError(Exception):
    pass
''' raise this when illegal line break occurs'''
    
def ErrorThrow(st):
    if debug_mode == True:
        print("test: ", st)
    raise CompileError(1002, st)

def ParamError(st):
    if debug_mode == True:
        print(st)
    raise CompileError(4000, st)


''' Internal compiler error. '''
def ICE(st="assertion failed"):
    if debug_mode == True:
        print(st)
        traceback.print_stack()
    raise CompileError(9999, "Internal Compiler Error: "+st)


''' Type mismatch error. '''
def ThrowTypeMismatch(lineno: int, expected: str="int", found: str="qbit"):
    ErrorThrow('in line {}, type mismatch (expected \'{}\', found \'{}\')'.format(lineno, expected, found))

''' Undefined variable error.'''
def ThrowUndefinedVariable(lineno: int, var_name: str):
    ErrorThrow('in line {}, undefined variable \'{}\''.format(lineno, var_name))
''' Redefined variable error.'''
def ThrowRedefinedVariable(lineno: int, var_name: str):
    ErrorThrow('in line {}, redefined  variable \'{}\''.format(lineno, var_name))
''' Bad loop range error.'''
def ThrowLoopRangeUnknown(lineno: int):
    ErrorThrow('in line {}, loop range upper and lower bound must be known\'{}\''.format(lineno))

''' Division by zero error. '''
def ThrowDivisionByZero(pos: str):
    ErrorThrow('in {}, integer divided by 0.'.format(pos))

''' Out of bound error. '''
def ThrowArrayOutOfBound(pos: str, index: int, arr: str, size: int):
    ErrorThrow('in {}, array index ({}) out of bound for {}[{}]'.format(pos, index, arr, size))

''' Bulk operation size mismatch error. '''
def ThrowBulkSizeMismatch(pos: str, sizes: T.List[int]):
    ErrorThrow('in {}, bulk ops size mismatch ({})'.format(pos, sizes))

''' Operation on same qubit error. '''
def ThrowDuplicateQubit(pos: str):
    ErrorThrow('in {}, multi-qubit operation accesses duplicate qubit'.format(pos))


''' Already measured error. '''
def ThrowAlreadyMeasured(pos: str, arr: str, index: T.Optional[int] = None):
    if index==None:
        ErrorThrow('in {}, qubit {} used after measured.'.format(pos, arr))
    else:
        ErrorThrow('in {}, qubit {}[{}] used after measured.'.format(pos, arr, index))

def ThrowMappingError(msg: str):
    raise MappingError(msg)


class CompileError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

class CoreError(Exception):

    def __init__(self, msg):
        self.msg = "core error: "+msg

class MappingError(Exception):

    def __init__(self, msg):
        self.msg = "qubit mapping error: "+msg