from numpy import pi
from isq.globalVar import isq_env
try:
    from braket.circuits import Circuit
    isq_env.set_env('aws', True)
except:
    pass

QCIS_TO_AWS = {
    'H': 'h',
    'X': 'x',
    'Y': 'y',
    'Z': 'z',
    'S': 's',
    'T': 't',
    'SD': 'si',
    'TD': 'ti',
    'CZ': 'cz',
    'CX': 'cnot',
    'CY': 'cy',
    'CNOT': 'cnot',
    'RX': 'rx',
    'RY': 'ry',
    'RZ': 'rz',
}

def translate_to_qcis(isq_ir):

    res = []
    for qcis in isq_ir.split('\n'):
        qcis = qcis.strip()
        if qcis:
            qcis_tmp = qcis.split(' ')
            gate = qcis_tmp[0]
            if gate in ['CX', 'CNOT']:
                res.append(f'Y2P {qcis_tmp[2]}')
                res.append(f'CZ {qcis_tmp[1]} {qcis_tmp[2]}')
                res.append(f'Y2M {qcis_tmp[2]}')
            elif gate == 'CY':
                res.append(f'Y2P {qcis_tmp[2]}')
                res.append(f'CZ {qcis_tmp[1]} {qcis_tmp[2]}')
                res.append(f'Y2M {qcis_tmp[2]}')
                res.append(f'CZ {qcis_tmp[1]} {qcis_tmp[2]}')
            else:
                res.append(qcis)
    return "\n".join(res)

def translate_to_aws(isq_ir):
    
    if not isq_env.get_env('aws'):
        raise "aws is not support in this env, please `pip install amazon-braket-sdk`"

    circuit = Circuit()
    q_cnt = 0
    q_map = {}
    q_measure = []

    for qcis in isq_ir.split('\n'):
        qcis = qcis.strip()
        if qcis:
            qcis_tmp = qcis.split(' ')
            gate = qcis_tmp[0]
            
            if qcis_tmp[1] not in q_map:
                q_map[qcis_tmp[1]] = q_cnt
                q_cnt += 1
            if gate in ['CZ', 'CX', 'CNOT']:
                if qcis_tmp[2] not in q_map:
                    q_map[qcis_tmp[2]] = q_cnt
                    q_cnt += 1

            if gate == 'H':
                circuit.h(q_map[qcis_tmp[1]])
            elif gate == 'X':
                circuit.x(q_map[qcis_tmp[1]])
            elif gate == 'Y':
                circuit.y(q_map[qcis_tmp[1]])
            elif gate == 'Z':
                circuit.z(q_map[qcis_tmp[1]])
            elif gate == 'S':
                circuit.s(q_map[qcis_tmp[1]])
            elif gate == 'T':
                circuit.t(q_map[qcis_tmp[1]])
            elif gate == 'SD':
                circuit.si(q_map[qcis_tmp[1]])
            elif gate == 'TD':
                circuit.ti(q_map[qcis_tmp[1]])
            elif gate == 'CZ':
                circuit.cz(q_map[qcis_tmp[1]], q_map[qcis_tmp[2]])
            elif gate == 'CY':
                circuit.cy(q_map[qcis_tmp[1]], q_map[qcis_tmp[2]])
            elif gate == 'CX':
                circuit.cnot(q_map[qcis_tmp[1]], q_map[qcis_tmp[2]])
            elif gate == 'CNOT':
                circuit.cnot(q_map[qcis_tmp[1]], q_map[qcis_tmp[2]])
            elif gate == 'RX':
                circuit.rx(q_map[qcis_tmp[1]], float(qcis_tmp[2]))
            elif gate == 'RY':
                circuit.ry(q_map[qcis_tmp[1]], float(qcis_tmp[2]))
            elif gate == 'RZ':
                circuit.rz(q_map[qcis_tmp[1]], float(qcis_tmp[2]))
            elif gate == 'X2M':
                circuit.rx(q_map[qcis_tmp[1]], -pi / 2)
            elif gate == 'X2P':
                circuit.rx(q_map[qcis_tmp[1]], pi / 2)
            elif gate == 'Y2M':
                circuit.ry(q_map[qcis_tmp[1]], -pi / 2)
            elif gate == 'Y2P':
                circuit.ry(q_map[qcis_tmp[1]], pi / 2)
            elif gate == 'M':
                q_measure.append(q_map[qcis_tmp[1]])
        
    return circuit, q_measure


def split_rotation_gates(qir):
    ir_list = qir.split("\n")
    ir_list_copy = ir_list.copy()
    for i, ir in enumerate(ir_list):
        if any([ir.startswith("RX"), ir.startswith("RY"), ir.startswith("RZ")]):
            ir_list_copy_list = ir_list_copy[i].split()
            if float(ir_list_copy_list[2]) > pi or float(ir_list_copy_list[2]) < -pi:
                ir_list_copy_list_new = ir_list_copy_list.copy()
                ir_list_copy_list_new[2] = str(float(ir_list_copy_list[2]) / 2)
                ir_list_copy_new = " ".join(ir_list_copy_list_new)
                new_str = ir_list_copy_new + "\n" + ir_list_copy_new
                ir_list_copy[i] = new_str
    return "\n".join(ir_list_copy)