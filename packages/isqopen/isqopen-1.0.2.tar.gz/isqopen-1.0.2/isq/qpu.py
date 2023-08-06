from isq.device.device import Device
from .quantum import quantumCor

class qpu():
    
    def __init__(self, device: Device):
        self._device = device
    
    def __call__(self, f):
        cor = quantumCor(f, self._device)
        return cor