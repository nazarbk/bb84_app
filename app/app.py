import streamlit as st
from bb84 import generate_alice_data, create_alice_qubits, measure_qubits, extract_shared_key, detect_eavesdropper, apply_eavesdropper
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="BB84 Interactive Simulation", 
    page_icon="assets/favicon.png",
    layout="centered"
)
st.title("🔐 BB84 Protocol - Be Bob!")
st.markdown("Simulate BB84 step by step and understand quantum key distribution.")

# --------------------------------
# Explanation of the BB84 Protocol 
# --------------------------------

with st.expander("🔍 What is the BB84 Protocol"):
    st.markdown("""
    The **BB84 Protocol** is a quantum key distribution (QKD) protocol that allows two parties, Alice and Bob, to establish a secret shared key over a public channel.


    ### How it works:

    1. **Alice generates a random sequence of bits** (0s and 1s) and encodes them in quantum states using random bases (Z and X).
    - **Z basis** (computacional basis):
        - Bit 0 → |0⟩ 
        - Bit 1 → |1⟩ 
    - **X basis** (diagonal basis):
        - Bit 0 → |+⟩
        - Bit 1 → |-⟩

    2. **Bob receives the qubits** and measures them using his own randomly chosen bases (Z or X). He doesn't know Alice's bases, so the measurement outcome might not match Alice's bit. 

    3. **Alice and Bob compare their bases** (not the bits) publicly. If they used same basis, they keep the measured bit.
    - This gives them a shared sequence of bits, which forms the secret key.

    4. **Eavesdropping detection**: If someone (Eve) tries to intercept the qubits, the measurements will be altered, and discrepancies will be detected when Alice and Bob compare their bits.

    This ensures that the secret key remains secure.

    ### Why it is secure?
    The security of the BB84 protocol relies on the principles of **quantum mechanics**, where measuring a quantum state alters it. Any attempt to intercept the qubits by an eavesdropper introduces detectable discrepancies.

    Read more about the BB84 protocol on [Wikipedia](https://en.wikipedia.org/wiki/BB84).
    """)

st.subheader("🧠 Step 1: Alice generates random bits and bases")
st.info("""
Alice wants to send a secret key. She starts by generating a random sequence of bits, and a random sequence of bases (Z or X). Each bit is encoded into a qubit according to its base. 
""")


# --------------------------
# Step 0: Slider - Control n 
# --------------------------

# Let user select number of qubits
n = st.slider("Number of qubits to simulate", min_value=4, max_value=64, value=8, step=2)

# Reset everything when the number of qubits changes
if "n_committed" in st.session_state and st.session_state["n_committed"] != n:
    for key in ["alice_committed", "bob_committed", "eve_committed",
                "alice_bits", "alice_bases", "alice_qubits",
                "bob_bases", "bob_results",
                "alice_qubits_eve", "eve_bases"]:
        st.session_state.pop(key, None)
st.session_state["n_committed"] = n

# -------------------
# Step 1: Alice
# -------------------

if st.button("Generate Alice's bits and bases"):
    bits, bases = generate_alice_data(n)
    st.session_state["alice_bits"] = bits
    st.session_state["alice_bases"] = bases
    st.session_state["alice_qubits"] = create_alice_qubits(bits, bases)
    st.session_state["alice_committed"] = True
    # Reset Bob data when Alice regenerates
    for key in ["bob_committed", "eve_committed", "bob_bases", "bob_results", "alice_qubits_eve", "eve_bases"]:
        st.session_state.pop(key, None)

# Display Alice's data if available
if "alice_committed" in st.session_state:
    st.success("Alice's data has been generated.")
    st.markdown("Here are her randomly chosen bits and bases (normally secret):")
    st.table({
        "Bit (0/1)": st.session_state["alice_bits"],
        "Base (Z/X)": st.session_state["alice_bases"]
    })

# -------------------
# Step 2: Bob
# -------------------

if "alice_committed" in st.session_state:
    st.subheader("🎯 Step 2: Choose your measurement bases (as Bob)")
    st.info("""
    Bob receives the qubits from Alice, but he doesn't know the bases she used. So he chooses a base for each qubit (manually or randomly) and measures them.
    """)
    manual = st.radio("How Bob should choose his bases?", ["Manual", "Random"], horizontal=True)
    use_eve = st.checkbox("🕵️‍♀️ Activate eavesdropper (Eve)?", value=False)

    bob_bases = []
    cols = st.columns(5)

    for i in range(len(st.session_state["alice_bits"])):
        col = cols[i % 5]
        with col:
            if manual == "Manual":
                base = st.radio(f"Qubit {i}", ["Z", "X"], key=f"base_bob_{i}")
            else:
                if "bob_mode" not in st.session_state or st.session_state["bob_mode"] != "Random":
                    st.session_state["bob_bases"] = list(np.random.choice(["Z", "X"], size=n))
                    st.session_state["bob_mode"] = "Random"
                base = st.session_state["bob_bases"][i]
                st.radio(f"Qubit {i}", ["Z", "X"], index=0 if base == "Z" else 1, disabled=True, key=f"readonly_bob_{i}")
            bob_bases.append(base)

    # Reset next step if bases change
    if "bob_committed" in st.session_state and st.session_state.get("bob_bases") != bob_bases:
        for key in ["bob_committed", "eve_committed", "bob_results", "alice_qubits_eve", "eve_bases"]:
            st.session_state.pop(key, None)
    
    if st.button("Generate Bob's bases and measure"):
        if use_eve:
            eve_qubits, eve_bases = apply_eavesdropper(st.session_state["alice_qubits"])
            st.session_state["alice_qubits_eve"] = eve_qubits
            st.session_state["eve_bases"] = eve_bases
            st.warning("⚠️ Eve has intercepted the qubits before Bob measured them.")
            qubits_to_measure = eve_qubits
        else:
            qubits_to_measure = st.session_state["alice_qubits"]

        st.session_state["bob_bases"] = bob_bases
        st.session_state["bob_results"] = measure_qubits(qubits_to_measure, bob_bases)
        st.session_state["bob_committed"] = True
        st.success("✅ Bob has measured the qubits.")

# -----------------------
# Step 3: Detection + Key
# -----------------------

if "bob_committed" in st.session_state:
    st.subheader("🔐 Step 3: Shared Key Extraction & Security Check")
    st.info("""
    Now, Alice and Bob compare the bases they used. For each qubit where they used the **same base**, they keep the measured bit. Then, they publicly compare a few of those bits to check if someone (like Eve) has tampered with the transmission.
    """)

    shared_key, matching_indices = extract_shared_key(
        st.session_state["alice_bases"],
        st.session_state["bob_bases"],
        st.session_state["bob_results"]
    )

    st.markdown(f"Number of matching bases: **{len(matching_indices)}**")

    sample_size = st.slider("How many matching bits to check publicly?", 1, min(20, len(matching_indices)), 5)
    sample_indices = sorted(np.random.choice(matching_indices, size=sample_size, replace=False))

    comparison_table = {
        "Index": sample_indices,
        "Bit (Alice)": [st.session_state["alice_bits"][i] for i in sample_indices],
        "Bit (Bob)": [st.session_state["bob_results"][i] for i in sample_indices],
    }

    if "eve_bases" in st.session_state:
        eve_results = measure_qubits(st.session_state["alice_qubits"], st.session_state["eve_bases"])
        comparison_table["Base (Eve)"] = [st.session_state["eve_bases"][i] for i in sample_indices]
        comparison_table["Bit (Eve)"] = [eve_results[i] for i in sample_indices]

    st.markdown("### Public comparison of selected positions:")
    st.table(comparison_table)

    discrepancies = detect_eavesdropper(st.session_state["alice_bits"], st.session_state["bob_results"], sample_indices)
    discrepancies = [int(i) for i in discrepancies]
    st.session_state["eve_committed"] = True

    st.markdown("### 🗝️ Final Shared Key")
    key_string = "".join(str(bit) for bit in shared_key)
    st.code(key_string)

    if discrepancies:
        st.warning(f"⚠️ Discrepancies detected at indices: {discrepancies}. Eve likely interfered. This key is NOT secure.")
    else:
        st.success("✅ No discrepancies found. The key is secure and can be used for encryption.")

# -----------------------
# Footer
# -----------------------
st.markdown("""
---

Developed by [Nazar Blanco](https://github.com/nazarbk)

Check out my other project: [Quantum Single Qubit Visualizer](https://quantum-single-qubit-visualizer.streamlit.app/)
""")