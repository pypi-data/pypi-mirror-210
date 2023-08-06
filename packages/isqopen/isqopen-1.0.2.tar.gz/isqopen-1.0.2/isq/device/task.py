try:
    from isq.globalVar import isq_env
    from braket.aws.aws_quantum_task import AwsQuantumTask
    isq_env.set_env('aws', True)
except:
    pass
from typing import Union
from logging import getLogger
from collections import defaultdict
class TaskType:
    QCSI = "QCIS"
    AWS = "AWS"

class TaskState:
    WAIT = "WAITING"
    COMPLETE = "COMPLETED"
    FAIL = "FAILED"
    CANCEL = "CANCELLED"

class ISQTask:

    NO_RESULT_TERMINAL_STATES = {TaskState.FAIL, TaskState.CANCEL}

    def __init__(
        self,
        task_id: Union[int, str],
        task_type,
        state,
        device,
        **kwargs,
    ) -> None:
        
        self._id = task_id
        self._type = task_type
        self._state = state
        self._res = {}
        self._device = device
        self.logger = getLogger(__name__)
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        if self._type == TaskType.AWS and self._state not in self.NO_RESULT_TERMINAL_STATES:
            if not isq_env.get_env('aws'):
                raise "aws is not support in this env, please `pip install amazon-braket-sdk`"

            self._task = AwsQuantumTask(self._id, poll_timeout_seconds = self._device._max_wait_time, logger=self.logger)
            self._measure = kwargs['measure']

    @property
    def state(self):
        return self._state

    def result(self):
        if self._state in self.NO_RESULT_TERMINAL_STATES:
            return {}

        if self._state == TaskState.COMPLETE: return self._res
        
        if self._type == TaskType.QCSI:
            m_res = self._device._account.query_experiment(self._id, max_wait_time = self._device._max_wait_time)
            if m_res:
                self.logger.info("任务执行成功")
                self._state = TaskState.COMPLETE
                ans = defaultdict(int)
                for t in m_res['results'][1:]:
                    x = ''.join([str(v) for v in t])
                    ans[x] += 1
                self._res = dict(ans)
            else:
                self.logger.info("任务执行中，请等待")
        
        if self._type == TaskType.AWS:
            state = self._task.state()
            if state in self.NO_RESULT_TERMINAL_STATES:
                self.logger.info("任务已失败或已取消")
                self._state = state
                return {}

            m_res = self._task.result()
            if m_res:
                self.logger.info("任务执行成功")
                mc = m_res.measurement_counts
                ans = {}
                # get measure qbit
                for k in mc:
                    rk = ''.join([k[i] for i in self._measure])
                    if rk not in ans: ans[rk] = 0
                    ans[rk] += mc[k]
                self._res = ans
                self._state = TaskState.COMPLETE
            else:
                self.logger.info("任务执行中，请等待")

        return self._res

    def cancel(self):

        if self._state == TaskState.WAIT:
            if self._type == TaskType.AWS:
                self._task.cancel()
                self._state = TaskState.CANCEL
