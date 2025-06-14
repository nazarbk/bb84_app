import streamlit as st
from bb84 import generate_alice_data, create_alice_qubits
import matplotlib.pyplot as plt

st.set_page_config(page_title="BB84 Interactive Simulation", layout="centered")

st.title("🔐 BB84 Protocol - Be Bob!")
st.markdown("Simulate receiving qubits, choose your measurement bases, and detect potential eavesdropping.")

st.subheader("Step 1: Alice generates random bits and bases")

n = st.slider("Number of qubits to simulate", min_value=4, max_value=64, value=8, step=2)

# Generate Alice data
if "alice_bits" not in st.session_state or "alice_bases" not in st.session_state or st.button("Generate"):
    bits, bases = generate_alice_data(n)
    st.session_state["alice_bits"] = bits
    st.session_state["alice_bases"] = bases
    st.success("Alice's data has been generated.")

# Show table
st.write("The following bits and bases have been generated:")

st.table({
    "Bit (0/1)": st.session_state["alice_bits"],
    "Base (Z/X)": st.session_state["alice_bases"]
})

st.subheader("Qubits prepared by Alice")

circuits = create_alice_qubits(
    st.session_state["alice_bits"],
    st.session_state["alice_bases"]
)

