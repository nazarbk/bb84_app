import numpy as np
from qiskit import QuantumCircuit
from typing import List

def generate_alice_data(n):
    bits = np.random.randint(2, size=n)
    bases = np.random.choice(["Z", "X"], size=n)
    return bits, bases

def create_alice_qubits(bits: List[int], bases: List[str]) -> List[QuantumCircuit]:
    circuits = []
    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if base == "X":
            qc.h(0)
        
        circuits.append(qc)
    
    return circuits
        

