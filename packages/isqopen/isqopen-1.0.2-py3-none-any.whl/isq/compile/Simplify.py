import re
import numpy as np
from cmath import *
import sys

def simplify(nQ,labT,labQ,labU):
    X = np.array([[0,1],[1,0]], dtype = complex)
    I = np.array([[1,0],[0,1]], dtype = complex)
    vh = np.sqrt(2)/2
    H = np.array([[vh,vh],[vh,-vh]],dtype=complex)
    numGate = len(labT)
    gateType = []
    C = np.eye(2**nQ, dtype = complex)
    for j in range(numGate):
        if labT[j] == 0:
            control = -1
            target = -1
            for k in range(nQ):
                if labQ[k,j] == 1:
                    control = k
                elif labQ[k,j] == -1:
                    target = k
            gateType.append('CNOT {},{}'.format(control,target))
            if control < target:
                dim_temp = 2**(target-control+1)
                temp = np.eye(dim_temp, dtype=complex)
                for l in range(dim_temp // 2, dim_temp, 2):
                    temp[l:l+2,l:l+2] = X[:,:]
                #print(dim_temp)
                if control > 0:
                    temp = np.kron(np.eye(2**control), temp)
                if target < nQ-1:
                    temp = np.kron(temp, np.eye(2**(nQ-target-1)))
                C =  temp @ C
                #print(temp)
            else:
                dim_temp = 2**(control-target+1)
                temp = np.eye(dim_temp, dtype=complex)
                for l in range(dim_temp // 2):
                    s = l*2+1
                    if s < dim_temp // 2:
                        t = s + dim_temp // 2
                        temp[s,t] = 1
                        temp[t,s] = 1
                        temp[s,s] = 0
                        temp[t,t] = 0
                #print(temp)
                if target > 0:
                    temp = np.kron(np.eye(2**target), temp)
                if control < nQ-1:
                    temp = np.kron(temp, np.eye(2**(nQ-control-1)))
                C = temp @ C
            #print('CNOT',control,target)
            #print(temp)
        else:
            target = -1
            for k in range(nQ):
                if labQ[k,j] == 1:
                    target = k
            temp = np.array([[1,0],[0,1]])
            if target == 0:
                temp = np.kron(labU[:,:,j], np.eye(2**(nQ-1)))
            elif target == nQ-1:
                temp = np.kron(np.eye(2**(nQ-1)), labU[:,:,j])
            else:
                temp = np.kron(np.eye(2**target), labU[:,:,j])
                temp = np.kron(temp, np.eye(2**(nQ-target-1)))
            #print(np.shape(C))
            #print(np.shape(temp))
            if very_close(labU[:,:,j],I):
                gateType.append('I')
            else:
                if labT[j] == 1:
                    gateType.append('RY {}'.format(target))
                elif labT[j] == 2:
                    val1 = labU[0,0,j]
                    val2 = labU[1,1,j]
                    theta = polar(val2)[1] - polar(val1)[1]
                    if isinstance(theta, complex):
                        #print(theta)
                        theta = theta.real
                    gateType.append('RZ({}) {}'.format(theta, target))
                else:
                    #print(C)
                    if very_close(labU[:,:,j], H):
                        gateType.append('H {}'.format(target))
                    else:
                        gateType.append('U {}'.format(target))
            C = temp @ C

                #print(temp)

    #print(gateType)
    return C, gateType

def Rz_gate(theta):
    return np.array([[np.exp(-theta*1j/2), 0],[0, np.exp(theta*1j/2)]], dtype=complex)

def Rx_gate(beta):
    return np.array([[np.cos(beta/2), -1j*np.sin((beta)/2)], [-1j*np.sin((beta)/2), np.cos((beta)/2)]])

def com_similar(c1, c2):
    if (c1.real-c2.real)**2+(c1.imag-c2.imag)**2 > 1e-6:
        return False
    return True

def very_close(A,B):
    assert np.shape(A) == np.shape(B)
    C = A - B
    err = sum(sum(np.abs(C)))
    if err < 1e-6:
        return True
    else:
        return False

def Rx(beta):
    return np.array([[np.cos(beta/2), -1j*np.sin((beta)/2)], [-1j*np.sin((beta)/2), np.cos((beta)/2)]])

def H():
    return 1/sqrt(2) * np.array([[1,1],[1,-1]])

def get_Ry_theta(U):
    nr,nc = U.shape
    assert (nr == 2) and (nc == 2)
    a,b,c,d = U[0,0],U[0,1],U[1,0],U[1,1]
    
    if np.abs(a) + np.abs(d) < 1e-5:
        return np.pi

    theta = 2*atan(c/a).real
    return round(theta, 4)


def single_decompose(U):
    nr,nc = U.shape
    assert (nr == 2) and (nc == 2)
    a,b,c,d = U[0,0],U[0,1],U[1,0],U[1,1]
    if np.abs(b) + np.abs(c) < 1e-4:
        gamma = 0
        alpha = polar(d/a)[1]
        if np.abs(alpha) < 1e-5:
            glist = [('I',0)]
        else:
            glist = [('RZ',alpha)]
    elif np.abs(a) + np.abs(d) < 1e-4:
        gamma = 0
        alpha = polar(c/b)[1]
        glist = [('RZ',alpha),('X',0)]
    else:
        #print('a,b,c,d = ',a,b,c,d)
        alpha = polar(sqrt(c*d/(a*b)))[1]
        gamma = polar(sqrt(b*d/(a*c)))[1]
        beta = np.arccos(2*a*d/(a*d-b*c) - 1)
        tm, theta = polar(sqrt(a*d-b*c))

        # a,b,c,d =  (-0.49999999918064497+0.49999999918064497j) (0.49999999836128994+0.49999999836128994j) (-0.30473785363145806-0.6380711876931069j) (0.638071184556266-0.30473785213332705j)

        #print(a,b,c,d)

        #print("==========U===========")
        #print(U)
        Up = tm*np.exp(1j*theta)*np.dot(np.dot(np.dot(Rz_gate(alpha),H()),np.dot(Rz_gate(beta),H())),Rz_gate(gamma))

        #print('Up ', Up)

        if not very_close(U, Up):
            #整体相位差-1，修改theta
            if very_close(U, -Up):
                #print("theta converse")
                theta += np.pi
            else:
                # ad相同，bc相位差-1，修改sin beta/2
                if com_similar(U[0,0], Up[0,0]):
                    #print("sin converse")
                    beta = -beta
                # bc相同，ad相位差-1，修改cos beta/2
                elif com_similar(U[0,1], Up[0,1]):
                    #print("cos converse")
                    beta = 2*np.pi - beta
                # a,b,c,d都差i或-i，讨论修改alpha或者gamma，通过bc确定
                elif com_similar(U[0,1], Up[0,1]*1j):
                    #print("gamma converse")
                    gamma += np.pi
                    #通过a再次判断是否修改修改cos beta / 2
                    if not com_similar(U[0,0], -Up[0,0]*1j):
                        #print("change beta")
                        beta = 2*np.pi - beta
                else:
                    #print("alpha converse")
                    alpha += np.pi
                    if not com_similar(U[0,0], -Up[0,0]*1j):
                        #print("change beta")
                        beta = 2*np.pi - beta



        glist = [('RZ',round(alpha,4)),('RX',round(beta, 4)),('RZ',round(gamma, 4))]

        U2 = (tm*np.exp(theta*1j)) * (Rz_gate(alpha) @ Rx_gate(beta) @ Rz_gate(gamma))
        #print('U',U)
        #print('alpha, beta, gamma = ',alpha,beta,gamma)
        #print(np.exp(alpha/2*1j), np.cos(beta/2), np.sin(beta/2)*1j, np.exp(gamma/2*1j))
        #print('U2',U2)
        flag = very_close(U, U2)
        if flag == False:
            print(Exception('single gate decomposition error here!'))
            sys.exit(0)
    return glist



def further_reduce_step1(nQ,gateSeq):
    gateLen = len(gateSeq)
    currentGate = ['' for i in range(nQ)]
    results = []
    for i in range(gateLen):
        gate = [gateSeq[i][0], gateSeq[i][1], gateSeq[i][2]]
        if gate[0] == 'I':
            continue
        if gate[0] == 'RZ':
            theta = gate[1]
            if isinstance(theta, complex):
                theta = theta.real
            if theta <= 0:
                theta = theta + np.pi*2

            theta = theta*180/np.pi
            if np.abs(theta-45) < 1e-6:
                gate[0] = 'T'
            elif np.abs(theta-90) < 1e-6:
                gate[0] = 'S'
            elif np.abs(theta-180) < 1e-6:
                gate[0] = 'Z'
            elif np.abs(theta-360) < 1e-6:
                gate[0] = 'I'
                #print(i)
                continue
                
            #theta = int(round(theta*10))
            theta = round(theta*np.pi / 180, 4)
            gate = (gate[0], theta, gate[2])
            results.append(tuple(gate))
        elif gate[0] == 'RX':
            theta = gate[1]
            if isinstance(theta, complex):
                theta = theta.real
            if theta <= 0:
                theta = theta + np.pi*2

            if np.abs(theta - 2*np.pi) < 1e-6:
                gate[0] = 'I'
                continue
            elif np.abs(theta-np.pi) < 1e-6:
                gate[0] = 'X'

            gate = (gate[0], round(theta, 4), gate[2])
            results.append(tuple(gate))

        elif gate[0] == 'RY':
            theta = gate[1]
            if isinstance(theta, complex):
                theta = theta.real
            if theta <= 0:
                theta = theta + np.pi*2

            if np.abs(theta - 2*np.pi) < 1e-6:
                gate[0] = 'I'
                continue
            elif np.abs(theta-np.pi) < 1e-6:
                gate[0] = 'Y'

            gate = (gate[0], round(theta, 4), gate[2])
            results.append(tuple(gate))            

        elif gate[0] == 'CNOT':
            c,t = gate[2]
            #results.append(('H', 0, t))
            #results.append(('CZ', 0, (c,t)))
            #results.append(('H', 0, t))
            results.append(('CNOT', 0, (c,t)))
        else: # H or X or Z
            results.append(tuple(gate))
    #print(results)
        if len(results) > 1 and results[-1] == results[-2]:
            results.pop(-1)
            results.pop(-1)
            
    return results

def further_reduce_step2(data):
    
    lineData = data.split('\n')
    newlineData = []
    
    position = 1
    newlineData.append(lineData[0])
    while position < len(lineData):
        if newlineData and newlineData[-1] == lineData[position]:
            if (lineData[position][:1] in ['X','Y','Z','H','S','T']) or (lineData[position][:4] == 'CNOT'):
                newlineData.pop(-1)
        else:
            newlineData.append(lineData[position])
        
        position = position + 1
    
    return "\n".join(newlineData)

def direct_sum(a, b):
    na, ma = a.shape
    nb, mb = b.shape
    c = np.matrix(np.zeros((na + nb, ma + mb), dtype = np.complex64))
    for x in range(na):
        for y in range(ma):
            c[x, y] = a[x, y]
    for x in range(nb):
        for y in range(mb):
            c[x + na, y + ma] = b[x, y]
    return c

'''
labU: numpy.ndarray [2**n, 2**n, numU]
    the i-th unitary is labU[:, :, i-1]
    
labT: numpy.ndarray [1, numU]

labT is type of gate:
0 : CNOT
1 : Ry-gate
2 : Rz-gate
3 : arbitrary single-qubit gate

labQ is the qubit index the gate applied on:
    for single_qubit gate, labQ[k-1,j-1] means j-th gate is applied on k-th qubit.
    for CNOT, 1 means control, -1 means target
'''
