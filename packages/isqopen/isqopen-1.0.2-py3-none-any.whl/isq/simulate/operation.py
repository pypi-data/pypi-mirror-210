from autograd import numpy as anp
from isq.globalVar import isq_env

try:
    from jax import numpy as jnp
    isq_env.set_env('jax', True)
except:
    pass

try:
    import torch
    isq_env.set_env('torch', True)
except:
    pass
# 0: anp; 1: jnp; 2: torch
np_mod = 0

def set_mod(mod):
    global np_mod
    if isq_env.get_env('jax') or isq_env.get_env('torch'): np_mod = mod

def reshape_single(state, qnum, target):
    shape = [1 << target, 2, 1 << (qnum - 1 - target)]
    if np_mod == 1: return jnp.reshape(state, shape)
    elif np_mod == 2: return torch.reshape(state, shape)
    return anp.reshape(state, shape)

def reshape_double(state, qnum, t1, t2):
    shape = [1 << t1, 2, 1 << (t2 - t1-1), 2, 1 << (qnum - t2 - 1)]
    if np_mod == 1: return jnp.reshape(state, shape)
    elif np_mod == 2: return torch.reshape(state, shape)
    return anp.reshape(state, shape)

def X():
    if np_mod == 1: return jnp.array([[0,1], [1,0]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[0,1], [1,0]], dtype=torch.cfloat)
    return anp.array([[0,1], [1,0]], dtype=complex)
def Y():
    if np_mod == 1: return jnp.array([[0,-1j], [1j,0]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[0,-1j], [1j,0]], dtype=torch.cfloat)
    return anp.array([[0,-1j], [1j,0]], dtype=complex)
def Z():
    if np_mod == 1: return jnp.array([[1,0], [0,-1]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[1,0], [0,-1]], dtype=torch.cfloat)
    return anp.array([[1,0], [0,-1]], dtype=complex)
def H():
    if np_mod == 1: return 1/jnp.sqrt(2) * jnp.array([[1,1], [1,-1]], dtype=complex)
    elif np_mod == 2: return 1/torch.sqrt(torch.tensor(2)) * torch.tensor([[1,1], [1,-1]], dtype=torch.cfloat)
    return 1/anp.sqrt(2) * anp.array([[1,1], [1,-1]], dtype=complex)
def T():
    if np_mod == 1: return jnp.array([[jnp.exp(-1j*jnp.pi / 8),0], [0,jnp.exp(1j*jnp.pi / 8)]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[torch.exp(torch.tensor(-1j*torch.pi / 8)),0], [0,torch.exp(torch.tensor(1j*torch.pi / 8))]], dtype=torch.cfloat)
    return anp.array([[anp.exp(-1j*anp.pi / 8),0], [0,anp.exp(1j*anp.pi / 8)]], dtype=complex)
def S():
    if np_mod == 1: return jnp.array([[1,0], [0,1j]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[1,0], [0,1j]], dtype=torch.cfloat)
    return anp.array([[1,0], [0,1j]], dtype=complex)
def TD():
    if np_mod == 1: return jnp.array([[jnp.exp(1j*jnp.pi / 8),0], [0,jnp.exp(-1j*jnp.pi / 8)]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[torch.exp(torch.tensor(1j*torch.pi / 8)),0], [0,torch.exp(torch.tensor(-1j*torch.pi / 8))]], dtype=torch.cfloat)
    return anp.array([[anp.exp(1j*anp.pi / 8),0], [0,anp.exp(-1j*anp.pi / 8)]], dtype=complex)
def SD():
    if np_mod == 1: return jnp.array([[1,0], [0,-1j]], dtype=complex)
    elif np_mod == 2: return torch.tensor([[1,0], [0,-1j]], dtype=torch.cfloat)
    return anp.array([[1,0], [0,-1j]], dtype=complex)
def RX(theta):
    if np_mod == 1:
        theta /= 2
        return jnp.array([[jnp.cos(theta),-1j*jnp.sin(theta)],[-1j*jnp.sin(theta),jnp.cos(theta)]], dtype=complex)
    elif np_mod == 2:
        theta_ = torch.div(theta, 2).reshape(-1)
        return torch.cat((torch.cos(theta_),-1j*torch.sin(theta_),-1j*torch.sin(theta_),torch.cos(theta_))).reshape(2, 2).type(torch.cfloat)
    elif np_mod == 0:
        theta /= 2
        return anp.array([[anp.cos(theta),-1j*anp.sin(theta)],[-1j*anp.sin(theta),anp.cos(theta)]], dtype=complex)
def RY(theta):
    if np_mod == 1:
        theta /= 2
        return jnp.array([[jnp.cos(theta),-1*jnp.sin(theta)],[jnp.sin(theta),jnp.cos(theta)]], dtype=complex)
    elif np_mod == 2:
        theta_ = torch.div(theta, 2).reshape(-1)
        return torch.cat((torch.cos(theta_),-1*torch.sin(theta_),torch.sin(theta_),torch.cos(theta_))).reshape(2, 2).type(torch.cfloat)
    elif np_mod == 0:
        theta /= 2
        return anp.array([[anp.cos(theta),-1*anp.sin(theta)],[anp.sin(theta),anp.cos(theta)]], dtype=complex)
def RZ(theta):
    if np_mod == 1:
        theta /= 2
        return jnp.array([[jnp.exp(-1j*theta),0],[0,jnp.exp(1j*theta)]], dtype=complex)
    elif np_mod == 2:
        theta_ = torch.div(theta, 2).reshape(-1)
        return torch.cat((torch.exp(-1j*theta_),torch.zeros(1),torch.zeros(1),torch.exp(1j*theta_))).reshape(2, 2).type(torch.cfloat)
    if np_mod == 0:
        theta /= 2
        return anp.array([[anp.exp(-1j*theta),0],[0,anp.exp(1j*theta)]], dtype=complex)
def X2P():
    if np_mod == 1: return jnp.sqrt(2)/2 * jnp.array([[1, -1j], [-1j, 1]], dtype=complex)
    elif np_mod == 2: return torch.sqrt(torch.tensor(2))/2 * torch.tensor([[1, -1j], [-1j, 1]], dtype=torch.cfloat)
    return anp.sqrt(2)/2 * anp.array([[1, -1j], [-1j, 1]], dtype=complex)
def X2M():
    if np_mod == 1: return jnp.sqrt(2)/2 * jnp.array([[1, 1j], [1j, 1]], dtype=complex)
    elif np_mod == 2: return torch.sqrt(torch.tensor(2))/2 * torch.tensor([[1, 1j], [1j, 1]], dtype=torch.cfloat)
    return anp.sqrt(2)/2 * anp.array([[1, 1j], [1j, 1]], dtype=complex)
def Y2P():
    if np_mod == 1: return jnp.sqrt(2)/2 * jnp.array([[1, -1], [1, 1]], dtype=complex)
    elif np_mod == 2: return torch.sqrt(torch.tensor(2))/2 * torch.tensor([[1, -1], [1, 1]], dtype=torch.cfloat)
    return anp.sqrt(2)/2 * anp.array([[1, -1], [1, 1]], dtype=complex)
def Y2M():
    if np_mod == 1: return jnp.sqrt(2)/2 * jnp.array([[1, 1], [-1, 1]], dtype=complex)
    elif np_mod == 2: return torch.sqrt(torch.tensor(2))/2 * torch.tensor([[1, 1], [-1, 1]], dtype=torch.cfloat)
    return anp.sqrt(2)/2 * anp.array([[1, 1], [-1, 1]], dtype=complex)


def single_gate(state, gate, qnum, target):
    #print(type(state))
    state = reshape_single(state, qnum, target)
    if gate == 'X':
        state = X() @ state[:,]
    elif gate == 'Y':
        state = Y() @ state[:,]
    elif gate == 'Z':
        state = Z() @ state[:,]
    elif gate == 'H':
        state = H() @ state[:,]
    elif gate == 'S':
        state = S() @ state[:,]
    elif gate == 'T':
        state = T() @ state[:,]
    elif gate == 'SD':
        state = SD() @ state[:,]
    elif gate == 'TD':
        state = TD() @ state[:,]
    elif gate == "X2M":
        state = X2M() @ state[:,]
    elif gate == "X2P":
        state = X2P() @ state[:,]
    elif gate == "Y2M":
        state = Y2M() @ state[:,]
    elif gate == "Y2P":
        state = Y2P() @ state[:,]

    if np_mod == 1: return jnp.ravel(state)
    elif np_mod == 2: return torch.ravel(state)
    return anp.ravel(state)


def single_rotate_gate(state, gate, qnum, target, theta):
    state = reshape_single(state, qnum, target)
    if gate == 'RX':
        state = RX(theta) @ state[:,]
    elif gate == 'RY':
        state = RY(theta) @ state[:,]
    elif gate == 'RZ':
        state = RZ(theta) @ state[:,]
    
    if np_mod == 1: return jnp.ravel(state)
    elif np_mod == 2: return torch.ravel(state)
    return anp.ravel(state)

def multi_gate(state, gate, qnum, ctrl, target):
    if ctrl < target:
        state = reshape_double(state, qnum, ctrl, target)
        if gate in ['CX', 'CNOT']:
            a,b = state[:,1,:,0,:], state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([b, a], axis = 2)
                state = jnp.stack([state[:,0,:,:,:], u], axis = 1)
            elif np_mod == 2:
                u = torch.stack([b, a], axis = 2)
                state = torch.stack([state[:,0,:,:,:], u], axis = 1)
            else:
                u = anp.stack([b, a], axis = 2)
                state = anp.stack([state[:,0,:,:,:], u], axis = 1)
        elif gate == 'CY':
            a,b = 1j*state[:,1,:,0,:], -1j*state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([b, a], axis = 2)
                state = jnp.stack([state[:,0,:,:,:], u], axis = 1)
            elif np_mod == 2:
                u = torch.stack([b, a], axis = 2)
                state = torch.stack([state[:,0,:,:,:], u], axis = 1)
            else:
                u = anp.stack([b, a], axis = 2)
                state = anp.stack([state[:,0,:,:,:], u], axis = 1)
        elif gate == 'CZ':
            a, b = state[:,0,:,1,:], -1*state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([a, b], axis = 1)
                state = jnp.stack([state[:,:,:,0,:], u], axis = 3)
            elif np_mod == 2:
                u = torch.stack([a, b], axis = 1)
                state = torch.stack([state[:,:,:,0,:], u], axis = 3)
            else:    
                u = anp.stack([a, b], axis = 1)
                state = anp.stack([state[:,:,:,0,:], u], axis = 3)

        if np_mod == 1: return jnp.ravel(state)
        elif np_mod == 2: return torch.ravel(state)
        return anp.ravel(state)
    else:
        state = reshape_double(state, qnum, target, ctrl)
        if gate in ['CX', 'CNOT']:
            a,b = state[:,0,:,1,:], state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([b, a], axis = 1)
                state = jnp.stack([state[:,:,:,0,:], u], axis = 3)
            elif np_mod == 2:
                u = torch.stack([b, a], axis = 1)
                state = torch.stack([state[:,:,:,0,:], u], axis = 3)                
            else:
                u = anp.stack([b, a], axis = 1)
                state = anp.stack([state[:,:,:,0,:], u], axis = 3)
        elif gate == 'CY':
            a,b = 1j*state[:,0,:,1,:], -1j*state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([b, a], axis = 1)
                state = jnp.stack([state[:,:,:,0,:], u], axis = 3)
            elif np_mod == 2:
                u = torch.stack([b, a], axis = 1)
                state = torch.stack([state[:,:,:,0,:], u], axis = 3)
            else:
                u = anp.stack([b, a], axis = 1)
                state = anp.stack([state[:,:,:,0,:], u], axis = 3)
        elif gate == 'CZ':
            a, b = state[:,0,:,1,:], -1*state[:,1,:,1,:]
            if np_mod == 1:
                u = jnp.stack([a, b], axis = 1)
                state = jnp.stack([state[:,:,:,0,:], u], axis = 3)
            elif np_mod == 2:
                u = torch.stack([a, b], axis = 1)
                state = torch.stack([state[:,:,:,0,:], u], axis = 3)
            else:
                u = anp.stack([a, b], axis = 1)
                state = anp.stack([state[:,:,:,0,:], u], axis = 3)
        
        if np_mod == 1: return jnp.ravel(state)
        elif np_mod == 2: return torch.ravel(state)
        return anp.ravel(state)

def swap(state, qnum, q1, q2):
    q1, q2 = min(q1, q2), max(q1, q2)
    state = reshape_double(state, qnum, q1, q2)
    a, b, c, d = state[:,0,:,0,:], state[:,0,:,1,:], state[:,1,:,0,:], state[:,1,:,1,:]
    if np_mod == 1:
        u = jnp.stack([a, c], axis = 2)
        v = jnp.stack([b, d], axis = 2)
        state = jnp.stack([u, v], axis = 1)
        return jnp.ravel(state)
    elif np_mod == 2:
        u = torch.stack([a, c], axis = 2)
        v = torch.stack([b, d], axis = 2)
        state = torch.stack([u, v], axis = 1)
        return torch.ravel(state)    
    else:
        u = anp.stack([a, c], axis = 2)
        v = anp.stack([b, d], axis = 2)
        state = anp.stack([u, v], axis = 1)
        return anp.ravel(state)

def measure(state, qnum, target):
    
    state = reshape_single(state, qnum, target)
    if np_mod == 1:
        p0 = jnp.real(jnp.sum(state[:, 0, :] * jnp.conj(state[:, 0, :])))
        res = 0
        if anp.random.uniform() < p0:
            state = state.at[:,1,:].set(0)
            state /= jnp.sqrt(p0)
        else:
            p1 = 1 - p0
            state = state.at[:,0,:].set(0)
            state /= jnp.sqrt(p1)
            res = 1
        state = jnp.ravel(state)
        return res, state
    elif np_mod == 2:
        p0 = torch.real(torch.sum(state[:, 0, :] * torch.conj(state[:, 0, :])))
        res = 0
        if anp.random.uniform() < p0:
            state[:,1,:] = 0
            state /= torch.sqrt(p0)
        else:
            p1 = 1 - p0
            state[:,0,:] = 0
            state /= torch.sqrt(p1)
            res = 1
        state = torch.ravel(state)
        return res, state
    else:
        p0 = anp.real(anp.sum(state[:, 0, :] * anp.conj(state[:, 0, :])))
        res = 0
        if anp.random.uniform() < p0:
            state[:,1,:] = 0
            state /= anp.sqrt(p0)
        else:
            p1 = 1 - p0
            state[:,0,:] = 0
            state /= anp.sqrt(p1)
            res = 1
        state = anp.ravel(state)
        return res, state

def shift(state, qnum, mq):

    qidx = {}
    idxq = {}
    for i in range(qnum):
        qidx[i] = i
        idxq[i] = i
    
    
    for i, m in enumerate(mq):
        if qidx[m] == i: continue
        state = swap(state, qnum, i, qidx[m])
        q = idxq[i]
        qidx[q] = qidx[m]
        qidx[m] = i
        idxq[i] = m
        idxq[qidx[q]] = q
    
    return state