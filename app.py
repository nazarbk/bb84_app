from bb84 import generate_alice_data, generate_bob_bases
import streamlit as st

st.set_page_config(page_title="BB84 Interactive Simulation", layout="centered")

st.title("🔐 BB84 Protocol: Be Bob!")
st.markdown("Simulate receiving qubits, choose your measurement bases, and detect potential eavesdropping.")

st.subheader("Step 1: Alice generates random bits and bases")

n = st.slider("Number of qubits to simulate", min_value=4, max_value=64, value=8, step=2)

if st.button("Generate Alice's bits and bases"):
    alice_data = generate_alice_data(n)
    st.session_state["alice_bits"] = alice_data["bits"]
    st.session_state["alice_bases"] = alice_data["bases"]
    st.success("Alice's data has been generated (kept hidden for now).")

if "alice_bits" in st.session_state and "alice_bases" in st.session_state:
    st.subheader("Step 2: Choose your measurement bases (as Bob)")

    bob_choice_mode = st.radio("How do you want to chose your bases?", ("Manual", "Random"))

    if bob_choice_mode == "Manual":
        bob_bases = []
        for i in range(n):
            base = st.selectbox(f"Qubit {i+1}: Choose basis", options=["Z (0)", "X (1)"], key=f"bob_base_{i}")
            bob_bases.append(0 if base == "Z (0)" else 1)
        st.session_state["bob_bases"] = bob_bases

    elif bob_choice_mode == "Random":
        bob_data = generate_bob_bases(n)
        st.session_state["bob_bases"] = bob_data.tolist()
        st.write("Random bases generated for Bob:")
        st.write(st.session_state["bob_bases"])