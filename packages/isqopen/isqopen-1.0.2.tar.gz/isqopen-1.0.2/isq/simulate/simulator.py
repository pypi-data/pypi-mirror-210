import os
import sys
from autograd import numpy as anp
import time
from isq.errors import *
from collections import defaultdict
from .operation import *
from isq.globalVar import isq_env

gate_list = ['H', 'X', 'Y', 'Z', 'S', 'T', 'RZ', 'RX', 'RY', 'SD', 'TD', 'X2M', 'X2P', 'Y2M', 'Y2P', 'CZ', 'CY', 'CX', 'CNOT', 'M']

def check(line_data):
    
    qdic = {}
    qnum = 0
    for idx, line in enumerate(line_data):
        line = line.strip()
        if not line:
            continue
        strArr = line.split(' ')
        if strArr[0] not in gate_list:
            raise CoreError('simulate error: in line {}, gate error'.format(idx))
        if len(strArr) < 2 or len(strArr) > 3:
            raise CoreError('simulate error: in line {}, qbit number error'.format(idx))
        if strArr[1][0] != 'Q' or not strArr[1][1:].isdigit():
            raise CoreError('simulate error: in line {}, qbit syntax error'.format(idx))

        if strArr[1] not in qdic:
            qdic[strArr[1]] = qnum
            qnum += 1
        
        if strArr[0] in ['CZ','CY','CX','CNOT']:
            if len(strArr) != 3:
                raise CoreError('simulate error: in line {}, qbit number error'.format(idx))
            
            if strArr[2][0] != 'Q' or not strArr[2][1:].isdigit():
                raise CoreError('simulate error: in line {}, qbit syntax error'.format(idx))

            if strArr[2] not in qdic:
                qdic[strArr[2]] = qnum
                qnum += 1
        if strArr[0] in ['RX', 'RY', 'RZ']:
            if len(strArr) != 3:
                raise CoreError('simulate error: in line {}, qbit number error'.format(idx))
    
    if qnum > 22:
        raise CoreError('simulate error: qbit number out of 22, can not simulate')

    return qnum, qdic

def getstate(line_data, qnum, qdic, mod, **kwargs):

    state = anp.zeros(pow(2, qnum), dtype = complex)
    state[0] = 1
    
    if mod == 1:
        if isq_env.get_env('jax'):
            state = jnp.zeros(jnp.power(2, qnum), dtype = complex)
            state = state.at[0].set(1)
        else:
            raise Exception('jax is not supported in this env, please install jax first!')
    elif mod == 2:
        if isq_env.get_env('torch'):
            state = torch.zeros(torch.pow(torch.tensor(2), torch.tensor(qnum)), dtype = torch.cfloat)
            state[0] = 1
        else:
            raise Exception('torch is not supported in this env, please install torch first!')

    mq = []
    for idx, line in enumerate(line_data):
        line = line.strip()
        if not line:
            continue
        strArr = line.split(' ')
        qid1 = qdic[strArr[1]]
        if strArr[0] == 'M':
            mq.append(qid1)
        else:
            if strArr[0] in ['CZ','CY','CX','CNOT']:
                qid2 = qdic[strArr[2]]
                state = multi_gate(state, strArr[0], qnum, qid1, qid2)
            elif strArr[0] in ['RX', 'RY', 'RZ']:
                state = single_rotate_gate(state, strArr[0], qnum, qid1, eval(strArr[2], kwargs))
            else:
                state = single_gate(state, strArr[0], qnum, qid1)
    
    return state, mq

def simulate(data, run_time = 100, fast = False, mod = 0):
    
    set_mod(mod)

    line_data = data.split('\n')

    qnum, qdic = check(line_data)

    ans = defaultdict(int)
    
    state, mq = getstate(line_data, qnum, qdic, mod)
    
    for iter_round in range(run_time):
        qvec = state.copy()
        res = ''
        for qidx in mq:
            mres, qvec = measure(qvec, qnum, qidx)
            res += str(mres)
        ans[res] += 1
    return ans


def getprobs(data, mod = 0, **kwargs):

    set_mod(mod)

    line_data = data.split('\n')

    qnum, qdic = check(line_data)

    state, mq = getstate(line_data, qnum, qdic, mod, **kwargs)
    state = shift(state, qnum, mq)

    if mod==1:
        state = state.conj() * state
        n = len(mq)
        state = jnp.reshape(state, [1 << n, 1 << (qnum - n)])
        
        return jnp.real(jnp.sum(state, axis = 1))

    elif mod==2:
        state = state.conj() * state
        n = len(mq)
        state = torch.reshape(state, [1 << n, 1 << (qnum - n)])
        
        return torch.real(torch.sum(state, axis = 1))

    else:
        state = anp.conj(state) * state
        n = len(mq)
        state = anp.reshape(state, [1 << n, 1 << (qnum - n)])
        
        return anp.real(anp.sum(state, axis = 1))



if __name__ == '__main__':
    # file_name = sys.argv[1];
    data = ''

    filename = 'output.txt'
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    testing_mode = True
    if testing_mode:
        file_in = open(filename,'r')
        data = file_in.read()
        file_in.close()
    else:
        try:
            while True:
                ssttrr = input()
                data = data + ssttrr + '\n'
        except EOFError:
            pass

    start_time = time.time()
    
    res = simulate(data, "test")
    if res['code'] == 0:
        print(res['data']['sim_res'])
    else:
        print(res)
    end_time = time.time()

