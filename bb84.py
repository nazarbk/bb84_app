import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from typing import List

def generate_alice_data(n):
    bits = np.random.randint(2, size=n)
    bases = np.random.choice(["Z", "X"], size=n)
    return bits, bases

def create_alice_qubits(bits, bases):
    circuits = []
    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if base == "X":
            qc.h(0)
        
        circuits.append(qc)
    
    return circuits
        

def measure_qubits(circuits, bob_bases):
    measured_results = []
    simulator = Aer.get_backend('qasm_simulator')

    for qc, base in zip(circuits, bob_bases):
        qc = qc.copy()
        if base == "X":
            qc.h(0)
        
        qc.measure(0, 0)

        qc_transpiled = transpile(qc, simulator)
        result = simulator.run(qc_transpiled, shots=1).result()
        
        measured_bit = int(list(result.get_counts().keys())[0])
        measured_results.append(measured_bit)

    return measured_results

def extract_shared_key(alice_bases, bob_bases, bob_results):
    shared_key = []
    matching_indices = []

    for i, (a, b) in enumerate(zip(alice_bases, bob_bases)):
        if a == b:
            shared_key.append(bob_results[i])
            matching_indices.append(i)

    return shared_key, matching_indices

def detect_eavesdropper(alice_bits, bob_bits, indices_to_check):
    discrepancies = []
    for i in indices_to_check:
        if alice_bits[i] != bob_bits[i]:
            discrepancies.append(i)
    return discrepancies


def apply_eavesdropper(alice_qubits):
    new_qubits = []
    eve_bases = []
    simulator = Aer.get_backend('qasm_simulator')

    for qc in alice_qubits:
        # Eve chooses a random base to measure
        eve_basis = np.random.choice(["Z", "X"])
        eve_bases.append(eve_basis)

        # Copy Alice's qubits and simulate Eve's measurement
        intercepted_qc = qc.copy()
        if eve_basis == "X":
            intercepted_qc.h(0)
        
        intercepted_qc.measure(0, 0)

        qc_transpiled = transpile(intercepted_qc, simulator)
        result = simulator.run(qc_transpiled, shots=1).result()
        
        measured_bit = int(list(result.get_counts().keys())[0])

        # Prepare new qubit based on Eve's measurement
        new_qc = QuantumCircuit(1, 1)
        if measured_bit == 1:
            new_qc.x(0)
        if eve_basis == "X":
            new_qc.h(0)
        
        new_qubits.append(new_qc)

    return new_qubits, eve_bases