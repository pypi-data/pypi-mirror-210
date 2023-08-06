from abc import ABC, abstractmethod
from isq.errors import *
from isq.compile.parser import IR, compile
from isq.config import debug_mode
from isq.simulate.simulator import simulate, getprobs
import random
from isq.quantum import quantumCor
from .translate import translate_to_aws, translate_to_qcis, split_rotation_gates
from .task import *
from .grad import optv
from isq.draw.drawer import Drawer
import logging
from isq.globalVar import isq_env

try:
    from ezQpy import *
    isq_env.set_env('qcis', True)
except:
    pass

try:
    from braket import aws
except:
    pass


def getRandom():
    s = ""
    for _ in range(10):
        s += chr(random.randint(97, 122))
    return s

class Device(ABC):

    def __init__(self, name, shots = 1000, max_wait_time = 600, logger=logging.getLogger(__name__)):
        self._name = name
        self._shots = shots
        self._max_wait_time = max_wait_time
        self._ir = ''
        self.logger = logger
        pass

    @abstractmethod
    def run(self, isq_str = '', file = None,  **kwargs):
        pass

    def get_ir(self):
        return self._ir
    
    def compile_to_ir(self, isq_str = '', file = None, target = "isq", **kwargs):
        
        args, kw = self.getargs(kwargs)
        kw.update(args)
        if file:
            with open(file, 'r') as f:
                isq_str = f.read()

        ir = IR()
        res = compile(ir, isq_str, target, quantumCor.getGate(), kw)
        if res == -1: raise CoreError(ir.error)
        res_ir = ir.out
        if target == 'qcis':
            res_ir = translate_to_qcis(res_ir)
        return res_ir
    
    def compile_with_par(self, isq_str = '', file = None, target = 'isq', **kwargs):

        args, kw = self.getargs(kwargs)
        if file:
            with open(file, 'r') as f:
                isq_str = f.read()
        
        ir = IR()
        res = compile(ir, isq_str, target, quantumCor.getGate(), kw, args)
        if res == -1: raise CoreError(ir.error)
        self._ir = ir.out
        return args

    def simulate(self, ir):
        return dict(simulate(ir, self._shots))
    
    def getargs(self, kwargs):
        args = {}
        kw = {}
        for k,v in kwargs.items():
            if isinstance(v, optv):
                args[k] = v._value
                v = v._value
            kw[k] = v
        return args, kw
    
    def draw_circuit(self, showparam=False):
        if self._ir:
            dw = Drawer(showparam=showparam)
            dw.plot(self._ir)

    @property
    def shots(self):
        return self._shots
    
    @property
    def max_wait_time(self):
        return self._max_wait_time
        

class LocalDevice(Device):

    def __init__(self, shots = 100, max_wait_time = 60, name = None, mode = 'fast', logger=logging.getLogger(__name__)):
        if name == None: name = "local_device"
        super().__init__(name, shots, max_wait_time, logger)
        
        if mode not in ['normal', 'fast']:
            raise CoreError('"{}" simulate mode is not support, only ["fast", "normal"]'.format(mode))
        self._mode = mode


    def run(self, isq_str = '', file = None, **kwargs):
        
        self._ir = self.compile_to_ir(isq_str, file, "isq", **kwargs)
        
        if self._mode == 'fast':
            return dict(simulate(self._ir, self._shots, fast = True))
        else:
            return dict(simulate(self._ir, self._shots, fast = False))
        
    def probs(self, isq_str = '', file = None, mod = 0, **kwargs):
        
        args = self.compile_with_par(isq_str, file, "isq", **kwargs)
        
        return getprobs(self._ir, mod, **args)

        


class QcisDevice(Device):

    def __init__(
        self,
        login_key = None,
        machine_name = None,
        shots = 1000,
        max_wait_time = 60,
        name = None,
        logger=logging.getLogger(__name__),
    ):
        if name == None: name = "qcis_device"
        
        if not isq_env.get_env('qcis'):
            raise Exception("ezQpy is not supported in this env, please install ezQpy first")

        super().__init__(name, shots, max_wait_time, logger)

        self._account = Account(login_key=login_key, machine_name=machine_name)
        self._qid = 0
    
    def run(
        self,
        isq_str = '',
        file = None,
        automap = False,
        init_map = None,
        **kwargs,
    ):

        qcis = self.compile_to_ir(isq_str, file, "qcis", **kwargs)
        #circuit = quantumCor.getMapping(12, [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12]], qcis)
        self._ir = qcis

        qcis_split_rotation_gates = split_rotation_gates(qcis)
        exp_name = "{}_{}".format(self._name, getRandom())
        query_id = self._account.submit_job(circuit=qcis_split_rotation_gates, exp_name=exp_name, version="1.0", num_shots=self._shots)
        if query_id:
            self.logger.info('qcis提交任务成功')
            return ISQTask(query_id, TaskType.QCSI, TaskState.WAIT, self)
        else:
            self.logger.error('qcis提交失败, 请确认硬件是否正常，或稍后再试')
            return ISQTask(0, TaskType.QCSI, TaskState.FAIL, self)


class AwsDevice(Device):

    def __init__(self, device_arn, s3, shots = 1000, max_wait_time = 60, name = None, logger=logging.getLogger(__name__)):
        
        if not isq_env.get_env('aws'):
            raise Exception("aws is not supported in this env, please `pip install amazon-braket-sdk`")
        
        if name == None: name = "aws_device"
        super().__init__(name, shots, max_wait_time, logger)

        #self._device = LocalSimulator()
        self._device = aws.AwsDevice(device_arn)
        self._s3_folder = s3

    
    def run(self, isq_str = '', file = None, **kwargs):

        isq_ir = self.compile_to_ir(isq_str, file, "isq", **kwargs)
        circuit, q_measure = translate_to_aws(isq_ir)
        self._ir = circuit
        try:
            task = self._device.run(circuit, self._s3_folder, shots=self._shots)
            #task = self._device.run(circuit, shots=self._shots)
            self.logger.info('aws提交任务成功')
            return ISQTask(task.id, TaskType.AWS, TaskState.WAIT, self, measure = q_measure, logger =self.logger)
            
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error('aws提交失败, 请确认硬件是否正常，或稍后再试')
            return ISQTask(0, TaskType.AWS, TaskState.FAIL, self)
