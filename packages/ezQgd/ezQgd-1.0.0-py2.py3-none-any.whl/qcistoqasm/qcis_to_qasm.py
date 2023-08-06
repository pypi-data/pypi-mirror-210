from .qcis import *
from .const import GATE_TRANSFORM


class QcisToQasm():
    def __init__(self):
        pass

    def get_gate_by_name(self, gate_name):
        gate = globals()[gate_name]
        return gate
    
    def find_qubit_idx_by_qasm(self, qcis):
        qubit_idx = re.findall(r'Q(\d+)', qcis)
        return qubit_idx

    def convert_qcis_to_qasm(
            self,
            qcis: str):
        """
            convert qasm to qcis

            Args:
                qcis: qcis

            Returns:
                str: return the converted qasm.
        """
        qcis = qcis.upper()
        qcis_instruction_list = qcis.split('\n')
        qcis_instruction_list = [
            inst.strip() for inst in qcis_instruction_list if qcis.strip()]
        qubit_idx = self.find_qubit_idx_by_qasm(qcis)
        qreg_qubit = max([int(idx) for idx in qubit_idx])
        qasm = f'''OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[{qreg_qubit}];\ncreg c[{qreg_qubit}];\n'''
        measure_qcis = ""
        for qcis_item in qcis_instruction_list:
            if not qcis_item:
                continue
            if qcis_item.startswith('M'):
                measure_qcis += f'{qcis_item}\n'
                continue
            gate = qcis_item.split(' ')[0]
            retrun_qasm = self.get_gate_by_name(gate)(qcis_item)
            qasm += retrun_qasm.__str__()
        measure_gate = GATE_TRANSFORM.get('M')
        qubit_list = self.find_qubit_idx_by_qasm(measure_qcis)
        for idx, qubit_idx in enumerate(qubit_list):
            qasm += f'{measure_gate} q[{int(qubit_idx) - 1}] -> c[{idx}];\n'
        return qasm

"""
if __name__ == "__main__":
    qcis = '''
        X Q1
        X Q1
        Y Q4
        Z Q4
        H Q4
        S Q4
        SD Q5
        T Q6
        TD Q6
        X2P Q6
        X2M Q6
        CZ Q1 Q2
        Y2P Q1
        Y2M Q1
        CZ Q4 Q5
        CZ Q9 Q10
        RZ Q2 2.135648
        RX Q2 -1.135648
        RY Q3 1.8567
        RXY Q7 3.2 1.04
        CZ Q12 Q14
        I Q1 100
        B Q6 Q2
        M Q7
        M Q5
        M Q1 Q2
    '''
    qcis_to_qasm = QcisToQasm()
    qasm = qcis_to_qasm.convert_qcis_to_qasm(qcis)
    print(qasm)
"""