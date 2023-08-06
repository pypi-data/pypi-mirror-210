from isq.errors import CompileError

t_EQ  = r'\=\='
t_LE  = r'\<\='
t_GE  = r'\>\='
t_NE = r'\!\='
t_KET_ZERO = r'\|0\>'
t_ignore = ' \t\r'

# 解析错误的时候直接抛出异常
def t_error(t):
    raise CompileError(1000, 'in line: {}, lex error at token : {}'.format(t.lineno, t.value[0]))
    #raise Exception('error {} at line {}'.format(t.value, t.lineno))

# 记录行号，方便出错定位
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# 支持c++风格的\\注释
def t_ignore_COMMENT(t):
    r'\/\/[^\n]*'

# 常数命令规则
def t_NUMBER(t):
    r'((?:0|(?:[1-9]\d*))(?:\.\d+)?)([i-j]?)'
    if ('i' in t.value) or ('j' in t.value):
        t.value = t.value.replace('i','j')
        t.value = complex(t.value)
    elif ('.' in t.value):
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


# 标识符的命令规则
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

reserved = {
    'if' : 'IF',
    #'then' : 'THEN',
    'else' : 'ELSE',
    #'fi' : 'FI',
    'for' : 'FOR',
    #'foreach' : 'FOREACH',
    'in' : 'IN',
    #'to' : 'TO',
    #'while' : 'WHILE',
    #'do'  :  'DO',
    #'od'  :  'OD',
    'procedure' : 'PROCEDURE',
    #'local' : 'LOCAL',
    'main' : 'MAIN',
    #'int' : 'INT',
    'qbit' : 'QBIT',
    'H' : 'H',
    'X' : 'X',
    'Y' : 'Y',
    'Z' : 'Z',
    'S' : 'S',
    'T' : 'T',
    'RX': 'RX',
    'RY': 'RY',
    'RZ': 'RZ',
    'CZ' : 'CZ',
    'CX' : 'CX',
    'CY' : 'CY',
    'CNOT': 'CNOT',
    'TD': 'TD',
    'SD': 'SD',
    'X2P': 'X2P',
    'X2M': 'X2M',
    'Y2P': 'Y2P',
    'Y2M': 'Y2M',
    'M' : 'M',
    'defgate' : 'DEFGATE'
    #'print' : 'PRINT',
    #'multipleGate' : 'MULTIPLEGATE',
    #'..' : 'RANGE'
    }

# 输入中支持的符号头token，当然也支持t_PLUS = r'\+'的方式将加号定义为token

literals = ['+','-','*','/','%', '<','>','=',',','(',')','[',']','{','}',';',':']

tokens = ['EQ','LE','GE', 'NE', 'ASSIGN','KET_ZERO','NUMBER','ID'] + list(reserved.values())
