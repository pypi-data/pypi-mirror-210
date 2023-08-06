import numpy as np
from scipy.linalg import svd, schur
# from numpy.linalg import svd, eig, qr, schur, diagonal

def _RyGate(angle):
    return np.array([[np.cos(angle / 2), -np.sin(angle / 2)], [np.sin(angle / 2), np.cos(angle / 2)]], dtype=complex)


def _RzGate(angle):
    return np.array([[np.exp(-1j * angle / 2), 0], [0, np.exp(1j * angle / 2)]], dtype=complex)

def PauliGate(angle, flag):
    if flag == 3:
        return _RzGate(angle)

    if flag == 2:
        return _RyGate(angle)


def mycsd(U):
    n = int(np.log2(U.shape[0]))
    U1 = U[0:2**(n-1),0:2**(n-1)]
    U2 = U[0:2**(n-1),2**(n-1):2**n]
    U3 = U[2**(n-1):2**n,0:2**(n-1)]
    U4 = U[2**(n-1):2**n,2**(n-1):2**n]
    
    A1, C, A2 = svd(U1)
    C = np.diag(C)
    S = U3 @ A2.conj().T
    #Q, R = qr(S, mode='complete')
    #S = np.diag(np.diag(R))
    ut, st, vt = svd(S)
    S = np.diag(st)
    #B1 = Q @ ut
    B1 = ut
    A2 = vt @ A2
    #C = C @ vt.conj().T
    C = vt @ C @ vt.conj().T
    #Q, R = qr(C, mode='complete')
    #C = np.diag(np.diag(R))
    #A1 = A1 @ Q
    A1 = A1 @ vt.conj().T
    B2 = -S @ A1.conj().T @ U2 + C @ B1.conj().T @ U4
    # print(A1 @ C @ A2 - U1)
    # print(C.conj().T @ C + S.conj().T @ S)
    
    return A1, B1, A2, B2, C, S

def labPauliGate(angle, target, nQ, flag):
    tempT = np.array([flag-1],dtype=int)
    tempQ = np.zeros([nQ,1],dtype=int)
    tempQ[target,0] = 1
    tempU = np.zeros([2,2,1],dtype=complex)
    tempU[:,:,0] = PauliGate(angle, flag)
    return tempT, tempQ, tempU

def labCNOT(control, target, nQ):
    tempT = np.array([0],dtype=int)
    tempQ = np.zeros([nQ,1], dtype=int)
    tempQ[control,0] = 1
    tempQ[target,0] = -1
    tempU = np.zeros([2,2,1],dtype=complex)
    tempU[:,:,0] = np.array([[0,1],[1,0]],dtype=complex)
    return tempT, tempQ, tempU

def labAND(labT, labQ, labU, tempT, tempQ, tempU):
    labT = np.r_[labT, tempT]
    labQ = np.c_[labQ, tempQ]
    labU = np.concatenate((labU, tempU), axis=2)
    return labT, labQ, labU

def Multiplexed(A, labQ_, nQ, flag):
    n = len(labQ_)
    if n == 1:
        labT, labQ, labU = labPauliGate(A[0], labQ_[0]-1, nQ, flag)
        
        return labT, labQ, labU
    
    A1 = A[0:2**(n-1):2]
    A2 = A[1:2**(n-1):2]
    B1 = (A1 + A2) / 2
    B2 = (A1 - A2) / 2
    if n == 2:
        labT, labQ, labU = labPauliGate(B1[0], labQ_[0]-1, nQ, flag)

        tempT, tempQ, tempU = labCNOT(labQ_[1]-1, labQ_[0]-1, nQ)
        labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

        tempT, tempQ, tempU = labPauliGate(B2[0], labQ_[0]-1, nQ, flag)
        labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

        tempT, tempQ, tempU = labCNOT(labQ_[1]-1, labQ_[0]-1, nQ)
        labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)
        
        return labT, labQ, labU
    
    C1 = B1[0:2**(n-2):2]
    C2 = B1[1:2**(n-2):2]
    D1 = (C1 + C2) / 2 
    D2 = (C1 - C2) / 2
    labT, labQ, labU = Multiplexed(D1, labQ_[0:n-2], nQ, flag)

    tempT, tempQ, tempU = labCNOT(labQ_[n-2]-1, labQ_[0]-1, nQ)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Multiplexed(D2, labQ_[0:n-2], nQ, flag)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = labCNOT(labQ_[n-1]-1, labQ_[0]-1, nQ)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    E1 = B2[0:2**(n-2):2]
    E2 = B2[1:2**(n-2):2]
    F1 = (E1 - E2) / 2
    F2 = (E1 + E2) / 2
    tempT, tempQ, tempU = Multiplexed(F1, labQ_[0:n-2], nQ, flag)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = labCNOT(labQ_[n-2]-1, labQ_[0]-1, nQ)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Multiplexed(F2, labQ_[0:n-2], nQ, flag)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = labCNOT(labQ_[n-1]-1, labQ_[0]-1, nQ)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    return labT, labQ, labU 

def Universal(nQ, labQ_, U):
    U = U.astype('complex')
    n = len(labQ_)
    if n == 1:
        labQ = np.zeros([nQ,1], dtype=int)
        labU = np.zeros([2,2,1], dtype=complex)
        labT = np.zeros([1,], dtype=int)
        labU[:,:,0] = U
        labT[0] = 3
        labQ[labQ_[0]-1,0] = 1

        return labT, labQ, labU
    
    A1, B1, A2, B2, C, S = mycsd(U)
    
    Dtemp, V1 = schur(A1 @ B1.conj().T)
    Dtemp = Dtemp.diagonal() 
    D1 = np.diag(Dtemp)
    D1 = D1 ** 0.5
    W1 = D1 @ V1.conj().T @ B1
    
    Dtemp, V2 = schur(A2 @ B2.conj().T)
    Dtemp = Dtemp.diagonal() 
    D2 = np.diag(Dtemp)
    D2 = D2 ** 0.5
    W2 = D2 @ V2.conj().T @ B2

    labT, labQ, labU = Universal(nQ, labQ_[1:n], W2)

    tempT, tempQ, tempU = Multiplexed(-2 * np.angle(np.diag(D2)), labQ_, nQ, 3)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Universal(nQ, labQ_[1:n], V2)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Multiplexed(2 * np.angle(np.diag(C) + 1j*np.diag(S)), labQ_, nQ, 2)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Universal(nQ, labQ_[1:n], W1)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Multiplexed(-2 * np.angle(np.diag(D1)), labQ_, nQ, 3)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    tempT, tempQ, tempU = Universal(nQ, labQ_[1:n], V1)
    labT, labQ, labU = labAND(labT, labQ, labU, tempT, tempQ, tempU)

    return labT, labQ, labU