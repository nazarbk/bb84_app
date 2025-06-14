from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

def generate_alice_data(n_bits: int) -> dict:
    """
    Generate random bits and bases for Alice.

    Parameters:
        n_bits (int): Number of bits/qubits to generate.
        
    Returns:
        dict: Dictionary with Alice's bits and bases.
    """

    bits = np.random.randint(2, size=n_bits)
    bases = np.random.randint(2, size=n_bits)
    return {
        "bits": bits,
        "bases": bases
    }

def generate_bob_bases(n_bits: int) -> np.ndarray:
    """
    Generate random measurement bases for Bob.

    Parameters:
        n_bits (int): Number of bits/qubits to measure.

    Returns:
        np.ndarray: Bob's random bases (0 = Z, 1 = X)
    """

    return np.random.randint(2, size=n_bits)

def measure_with_qiskit(alice_bits: list, alice_bases: list, bob_bases: list) -> list:
    """
    Simulate BB84 measurement using real quantum logic.

    Parameters:
        alice_bits (list): Bits sent by Alice.
        alice_bases (list): Bases used by Alice (0 = Z, 1 = X).
        bob_bases (list): Bases used by Bob (0 = Z, 1 = X).

    Returns:
        list: Bob's measurement results.
    """

    backend = Aer.get_backend('qasm_simulator')
    measurements = []

    for a_bit, a_base, b_base in zip(alice_bits, alice_bases, bob_bases):
        qc = QuantumCircuit(1, 1)

        # Step 1: Alice prepares the qubit
        if a_bit == 1:
            qc.x(0)
        if a_base == 1:
            qc.h(0)

        # Step 2: Bob prepares his measurement basis
        if b_base == 1:
            qc.h(0)
        
        # Step 3: Bob measures
        qc.measure(0, 0)

        result = backend.run(transpile(qc, backend), backend=backend, shots=1).result()
        measured_bit = int(list(result.get_counts().keys())[0])
        measurements.append(measured_bit)

    return measurements



------

from bb84 import generate_alice_data, generate_bob_bases, measure_with_qiskit
import streamlit as st

st.set_page_config(page_title="BB84 Interactive Simulation", layout="centered")

st.title("🔐 BB84 Protocol: Be Bob!")
st.markdown("Simulate receiving qubits, choose your measurement bases, and detect potential eavesdropping.")

st.subheader("Step 1: Alice generates random bits and bases")

prev_n = st.session_state.get("n_prev", None)
n = st.slider("Number of qubits to simulate", min_value=4, max_value=64, value=8, step=2)

# If n changed, reset all session data
if prev_n is not None and prev_n != n:
    for key in ["alice_bits", "alice_bases", "bob_bases", "bob_results"]:
        if key in st.session_state:
            del st.session_state[key]
    st.warning("Qubit number changed. Please regenerate Alice's data.")

st.session_state["n_prev"] = n

if st.button("Generate Alice's bits and bases"):
    alice_data = generate_alice_data(n)
    st.session_state["alice_bits"] = alice_data["bits"]
    st.session_state["alice_bases"] = alice_data["bases"]
    st.success("Alice's data has been generated (kept hidden for now).")

if "alice_bits" in st.session_state and "alice_bases" in st.session_state:
    st.subheader("Step 2: Choose your measurement bases (as Bob)")

    bob_choice_mode = st.radio("How do you want to chose your bases?", ("Manual", "Random"))

    if bob_choice_mode == "Manual":
        st.write("Click to choose your measurement basis for each qubit:")
        bob_bases = []

        for row in range(0, n, 6):
            row_end = min(row + 6, n)
            cols = st.columns(row_end - row)

            for i, col in enumerate(cols):
                with col:
                    qubit_index = row + i
                    base = st.radio(
                        label=f"Qubit {qubit_index + 1}",
                        options=["Z 🟦", "X 🟥"],
                        index=0,
                        key=f"bob_base_{qubit_index}",
                        horizontal=False

                    )
                    bob_bases.append(0 if base == "Z" else 1)

        st.session_state["bob_bases"] = bob_bases
            

    elif bob_choice_mode == "Random":
        if "bob_bases" not in st.session_state:
            bob_bases = generate_bob_bases(n)
            st.session_state["bob_bases"] = bob_bases.tolist()
        else:
            bob_bases = st.session_state["bob_bases"]

        st.write("Random bases generated for Bob:")
        
        bob_symbols = ["Z 🟦" if b == 0 else "X 🟥" for b in bob_bases]

        for row in range(0, n, 6):
            row_end = min(row + 6, n)
            cols = st.columns(row_end - row)

            for i, col in enumerate(cols):
                qubit_index = row + i
                col.markdown(
                    f"Qubit {qubit_index + 1} <br> {bob_symbols[qubit_index]}",
                    unsafe_allow_html=True
                )

if "alice_bits" in st.session_state and "alice_bases" in st.session_state and "bob_bases" in st.session_state:
    if st.button("Simulate Bob's Measurement"):
        alice_bits = st.session_state["alice_bits"]
        alice_bases = st.session_state["alice_bases"]
        bob_bases = st.session_state["bob_bases"]

        bob_results = measure_with_qiskit(alice_bits, alice_bases, bob_bases)
        st.session_state["bob_results"] = bob_results

        st.success("Measurement completed using Qiskit!")

        # Visual output
        st.markdown("Bob's Measured Bits:")
        for row in range(0, len(bob_results), 6):
            row_end = min(row + 6, len(bob_results))
            cols = st.columns(row_end - row)
            for i, col in enumerate(cols):
                index = row + i
                col.markdown(
                    f"Bit {index + 1}: {bob_results[index]}",
                    unsafe_allow_html=True
                )
