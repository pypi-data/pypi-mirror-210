from . import QSyn, Simplify
import numpy as np

def decompose(mat, rowS, current_ID, pos = None):

        # add position info
        posstr = ""
        if pos != None:
            posstr = "in line {}, ".format(pos)

        # decompose
        matrix = np.array(mat, dtype=complex)
        nq = int(np.log2(rowS))
        labQI = np.array(range(1,nq+1),dtype=int)


        if not Simplify.very_close(matrix @ matrix.conj().T, np.eye(rowS, dtype='complex')):
            return False, posstr + 'gate definition of ' + str(current_ID) + ': matrix not unitary.'

        labT, labQ, labU = QSyn.Universal(nq, labQI, matrix)
        matrix_C, gateType = Simplify.simplify(nq,labT,labQ,labU)


        if not Simplify.very_close(matrix, matrix_C):
            return False, posstr + 'gate definition of ' + str(current_ID) + ': decomposition error.'

        gateSeq = []
        for i in range(len(gateType)):
            st = gateType[i]
            if st[0:1] == 'I':
                continue
            if st[0:1] == 'H':
                ss = st.split(' ')[1]
                target = int(ss)
                gateSeq.append(('H', 0, target))
            if (st[0:1] == 'U'):
                #print(st[0:2])
                temp = Simplify.single_decompose(labU[:,:,i])
                ss = st.split(' ')[1]
                #print(labU[:,:,i])
                #print(temp)
                target = int(ss)
                for j in range(len(temp),0,-1):
                    ele = temp[j-1]
                    gateSeq.append((ele[0],ele[1],target))
            if (st[0:2] == 'RY'):
                theta = Simplify.get_Ry_theta(labU[:,:,i])
                ss = st.split(' ')[1]
                target = int(ss)
                gateSeq.append(('RY', theta, target))
            if (st[0:2] == 'RZ'):
                ss1,ss2 = st.split(' ')
                target = int(ss2)
                theta = float(ss1.lstrip('RZ(').rstrip(')'))
                gateSeq.append(('RZ',round(theta, 4),target))
            if (st[0:4] == 'CNOT'):
                ss = st.lstrip('CNOT')
                target1,target2 = ss.split(',')
                gateSeq.append( ('CNOT', 0, (int(target1),int(target2)) ) )

        gateSeq = Simplify.further_reduce_step1(nq, gateSeq)
        
        temp_I = np.eye(rowS, dtype = complex)
        if not Simplify.very_close(temp_I, matrix @ matrix.conj().T):
            return False, posstr + 'gate definition of ' + str(current_ID) + ': matrix not unitary.'
        
        return True, (nq, gateSeq, mat)