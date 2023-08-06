# -*- coding: utf-8 -*-

import numpy as np
from numpy.linalg import svd, eig, qr
import scipy as sp


def _diagk(X, k):
    return np.diag(X, k)


def _diagf(X):
    m, n = X.shape
    for i in range(m):
        for j in range(n):
            if i != j:
                X[i, j] = 0
    
    return X


def _diagp(Y, X, k):
    D = _diagk(X, k)
    j = np.nonzero(np.logical_or(np.real(D) < 0, np.imag(D) != 0))[0]
    D = np.diag(np.conj(D[j])/np.abs(D[j]))
    Y[:, j] = Y[:, j] @ D.conj().T
    X[j, :] = D @ X[j, :]
    X = X + 0
    return Y, X


def csd(Q1, Q2):
    m, p = Q1.shape
    n = Q2.shape[0]

    if m < n:
        V, U, Z, S, C = csd(Q2, Q1)
        C = C[:, p:0:-1]
        S = S[:, p:0:-1]
        Z = Z[:, p:0:-1]
        m = min(m, p)
        C[0 : m, :] = C[m:0:-1, :]
        U[:, 0 : m] = U[:, m:0:-1]
        n = min(n, p)
        S[0 : n, :] = S[n:0:-1, :]
        V[:, 0 : n] = V[:, n:0:-1]

        return U, V, Z, C, S
    
    U, C, Z = np.linalg.svd(Q1)
    Z = Z.conj().T

    q = min(m, p)
    temp = np.zeros([m, p])
    temp[0 : q, 0 : q] = np.diag(C)
    C = temp
    temp = C[0 : q, 0 :q]
    C[0 : q, 0 :q] = temp[::-1, ::-1]
    temp = U[:, 0 :q]
    U[:, 0 :q] = temp[:, ::-1]
    temp = Z[:, 0 :q]
    Z[:, 0 :q] = temp[:, ::-1]
    S = Q2 @ Z

    if q == 1:
        k = 0
    elif m < p:
        k = n
    else:
        k = np.r_[0, np.nonzero(np.diag(C) <= 1/np.sqrt(2))[0]+1].max()
    
    V, temp = np.linalg.qr(S[:, 0 : k], mode='complete')
    S = V.conj().T @ S
    r = min(k, m)
    S[:, 0 : r] = _diagf(S[:, 0 : r])
    if m == 1 and p > 1:
        S[0, 0] = 0
    
    if k < min(n, p):
        r = min(n, p)
        Ut, St, Vt = np.linalg.svd(S[k : n, k : r])
        temp = np.zeros([n-k, r-k])
        temp[0 : r-k+1, 0 : r-k+1] = np.diag(St)
        St = temp[0 : r-k+1, 0 : r-k+1]
        Vt = Vt.conj().T
        if k > 0:
            S[0 : k, k : r] = 0
        
        S[k : n, k : r] = St
        C[:, k : r] = C[:, k : r] @ Vt
        V[:, k : n] = V[:, k : n] @ Ut
        Z[:, k : r] = Z[:, k : r] @ Vt
        Q, R = np.linalg.qr(C[k : q, k : r], mode='complete')
        C[k : q, k : r] = _diagf(R)
        U[:, k : q] = U[:, k : q] @ Q

    if m < p:
        q = min(np.r_[np.nonzero(np.abs(_diagk(C,0))> 10*m*np.spacing(1))[0]+1, np.nonzero(np.abs(_diagk(S, 0)) > 10*n*np.spacing(1))[0]+1, np.nonzero(max(np.abs(np.r_[np.abs(S[:, m : p]),[],2])))[0]+1])

        maxq = m + n - p
        q = q + np.nonzero(max(np.r_[np.abs(S[:, q : maxq]),[],1]) > np.sqrt(np.spacing(1)))[0][0] + 1

        Q, R = np.linalg.qr(S[q : n, m : p], mode='complete')
        S[:, q : p] = 0
        S[q : n, m : p] = _diagf(R)
        V[:, q : n] = V[:, q : n] @ Q
        if n > 1:
            temp = C
            temp[:, 0 : p-m] = C[:, m : p]
            temp[:, p-m : p] = C[:, 0 : m]
            C = temp[:, 0 : p]
            temp = S
            temp[:, 0 : p-m] = S[:, m : p]
            temp[:, p-m : p] = S[:, 0 : m]
            S = temp
            temp[0 : p-m, :] = S[q : q+p-m, :]
            temp[p-m : p-m+q, :] = S[0 : q, :]
            temp[q+p-m : n, :] = S[q+p-m : n, :]
            S = temp[0 : n, 0 : p]
            temp = Z
            temp[:, 0 : p-m] = Z[:, m : p]
            temp[:, p-m : p] = Z[:, 0 : m]
            Z = temp[:, 0 : p]
            temp = V
            temp[:, 0 : p-m] = V[:, q : q+p-m]
            temp[:, p-m : q+p-m] = V[:, 0 : q]
            temp[:, q+p-m : n] = V[:, q+p-m : n]
            V = temp[:, 0 : n]
        else:
            temp = C
            temp[:, 0 : p-m] = C[:, m : p]
            temp[:, p-m : p] = C[:, 0 : m]
            C = temp[:, 0 : p]
            temp = S
            temp[:, 0 : p-m] = S[:, m : p]
            temp[:, p-m : p] = S[:, 0 : m]
            S = temp[0, 0 : p]
            temp = Z
            temp[:, 0 : p-m] = Z[:, m : p]
            temp[:, p-m : p] = Z[:, 0 : m]
            Z = temp[:, 0 : p]
            V = V[:, 0]
        
    if n < p:
        S[:, n : p] = 0
    
    U, C = _diagp(U, C, max(0, p-m))
    C = np.real(C)
    V, S = _diagp(V, S, 0)
    S = np.real(S)

    return U, V, Z, C, S

def gsvd(A, B):
    m = A.shape[0]
    n = B.shape[0]

    Q, R = np.linalg.qr(np.r_[A, B])
    U, V, Z, C, S = csd(Q[0 : m, :], Q[m : m+n, :])
    X = R.conj().T @ Z

    return U, V, X, C, S

def mycsd(U):
    n = int(np.log2(U.shape[0]))
    U1 = U[0:2**(n-1),0:2**(n-1)]
    U2 = U[0:2**(n-1),2**(n-1):2**n]
    U3 = U[2**(n-1):2**n,0:2**(n-1)]
    U4 = U[2**(n-1):2**n,2**(n-1):2**n]
    
    A1, C, A2 = svd(U1)
    C = np.diag(C)
    S = U3 @ A2.conj().T
    Q, R = qr(S, mode='complete')
    S = np.diag(np.diag(R))
    ut, st, vt = svd(S)
    S = np.diag(st)
    B1 = Q @ ut
    A2 = vt @ A2
    C = C @ vt.conj().T
    Q, R = qr(C, mode='complete')
    C = np.diag(np.diag(R))
    A1 = A1 @ Q
    B2 = -S @ A1.conj().T @ U2 + C @ B1.conj().T @ U4
    # print(A1 @ C @ A2 - U1)
    
    return A1, B1, A2, B2, C, S