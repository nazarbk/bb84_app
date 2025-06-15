import streamlit as st
from bb84 import generate_alice_data, create_alice_qubits, measure_qubits, extract_shared_key
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="BB84 Interactive Simulation", layout="centered")
st.title("🔐 BB84 Protocol - Be Bob!")
st.markdown("Simulate BB84 step by step and understand quantum key distribution.")

# -------------------
# Step 1: Alice
# -------------------

st.subheader("Step 1: Alice generates random bits and bases")

# Let user select number of qubits
n = st.slider("Number of qubits to simulate", min_value=4, max_value=64, value=8, step=2)

# Generate Alice data
if st.button("Generate Alice bits and bases"):
    bits, bases = generate_alice_data(n)
    st.session_state["alice_bits"] = bits
    st.session_state["alice_bases"] = bases
    st.success("Alice's data has been generated.")
    st.session_state["alice_qubits"] = create_alice_qubits(bits, bases)

    # Reset Bob data when Alice regenerates
    for key in ["bob_bases", "bob_results"]:
        if key in st.session_state:
            del st.session_state[key]

# Display Alice's data if available
if "alice_bits" in st.session_state:
    st.write("Alice's Bits and Bases")

    st.table({
        "Bit (0/1)": st.session_state["alice_bits"],
        "Base (Z/X)": st.session_state["alice_bases"]
    })

# -------------------
# Step 2: Bob
# -------------------

if "alice_bits" in st.session_state:
    st.subheader("Step 2: Choose your measurement bases (as Bob)")

    manual = st.radio("How you wanna choose your bases?", ["Manual", "Random"], horizontal=True)
   
    if manual == "Manual":
        # Gather manually selected bases
        bob_bases = []
        cols = st.columns(5)
        
        for i in range(len(st.session_state["alice_bits"])):
            col = cols[i % 5]
            with col:
                base = st.radio(
                    label = f"Qubit {i}",
                    options = ["Z", "X"],
                    key = f"base_bob_{i}"
                )
                bob_bases.append(base)
                
        st.session_state["bob_bases"] = bob_bases
        
    else:
        bob_bases = list(np.random.choice(["Z", "X"], size=len(st.session_state["alice_bits"])))
        st.session_state["bob_bases"] = bob_bases
        cols = st.columns(5)

        for i, base  in enumerate(bob_bases):
            col = cols[i % 5]
            with col:
                st.radio(
                    label=f"Qubit {i}",
                    options=[
                        base
                    ]
                )
    
    if st.button("Generate Bob's bases and measure"):
        st.session_state["bob_results"] =  measure_qubits(st.session_state["alice_qubits"], bob_bases)

        # Display results if available
        if "bob_bases" in st.session_state and "bob_results" in st.session_state:
            st.subheader("Bob's results")
            match_column = ["✅" if a == b and c == d else "❌" for a, b, c, d in zip(st.session_state["alice_bases"], st.session_state["bob_bases"], st.session_state["alice_bits"], st.session_state["bob_results"])] 

            # Display table comparision between Alice and Bob
            table_data = {
                "Bit (Alice)": st.session_state["alice_bits"],
                "Base (Alice)": st.session_state["alice_bases"],
                "Base (Bob)": st.session_state["bob_bases"],
                "Measurement (Bob)": st.session_state["bob_results"],
                "Match?": match_column
            }
            st.table(table_data)

