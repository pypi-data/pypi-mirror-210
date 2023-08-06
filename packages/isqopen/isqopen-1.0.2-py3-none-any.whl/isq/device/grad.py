from autograd import numpy as anp
from autograd.core import make_vjp as _make_vjp
from autograd.extend import vspace
from autograd.wrap_util import unary_to_nary
from isq.errors import CoreError
from collections import Iterable

class optv:
    def __init__(self, value = None):
        self._value = value

class optimizer:

    def __init__(self, lr, argnum = None):
        self._lr = lr
        self._args = argnum
        if self._args == None: self._args = [0]
    
    def opt(self, fun, *args):
    
        g = grad(fun, self._args)
        ds = g(*args)
        
        new_param = []
        for i in range(len(self._args)):
            params = args[self._args[i]]
            d = ds[i]

            if not isinstance(params, Iterable):
                new_param.append(params - self._lr * d)
                continue
            
            new_param_tmp = []
            for v, dv in zip(params, d):
                v -= self._lr * dv
                new_param_tmp.append(v)

            new_param.append(new_param_tmp)
            
        new_param.append(g.forward)

        return tuple(new_param)    
        

class grad:

    def __init__(self, fun, argnum = None):
        self._fun = fun
        self._arg = argnum
        if self._arg == None: self._arg = 0

        self._forward = 0

    @staticmethod
    @unary_to_nary
    def grad_with_forward(fun, x):
        vjp, ans = _make_vjp(fun, x)
        if not vspace(ans).size == 1: raise CoreError('Grad only applies to real scalar-output functions')
        grad_value = vjp(vspace(ans).ones())
        return grad_value, ans

    def __call__(self, *args, **kwargs):
        grad_fun = self.grad_with_forward(self._fun, self._arg)
        grad_value, ans = grad_fun(*args, **kwargs)
        self._forward = ans
        return grad_value

    @property
    def forward(self):
        return self._forward