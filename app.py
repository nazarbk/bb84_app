import streamlit as st
from bb84 import generate_alice_data, create_alice_qubits, measure_qubits, extract_shared_key, detect_eavesdropper, apply_eavesdropper
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="BB84 Interactive Simulation", layout="centered")
st.title("🔐 BB84 Protocol - Be Bob!")
st.markdown("Simulate BB84 step by step and understand quantum key distribution.")

st.subheader("🧠 Step 1: Alice generates random bits and bases")

# -------------------
# Step 0: Slider - Control n 
# -------------------

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
st.info("""
Alice wants to send a secret key. She starts by generating a random sequence of bits, and a random sequence of bases (Z or X). Each bit is encoded into a qubit according to its base. 
""")

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
    if "bob_committed" in st.session_state and st.session_state.get("bob_bases"):
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
        st.session_state["bob_results"] =  measure_qubits(qubits_to_measure, bob_bases)
        st.session_state["bob_committed"] = True
        st.success("✅ Bob has measured the qubits.")

# -------------------
# Step 3: Detection + Key
# -------------------

if "bob_committed" in st.session_state:
    st.header("🔐 Step 3: Shared Key Extraction & Security Check")
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
        "Bit (Bob)": [st.session_state["bob_results"][i] for i in sample_indices]
    }

    if "eve_bases" in st.session_state:
        eve_results = measure_qubits(st.session_state["alice_qubits"], st.session_state["eve_bases"])
        comparison_table["Base (Eve)"] = [st.session_state["eve_bases"][i] for i in sample_indices]
        comparison_table["Bit (Eve)"] = [eve_results[i] for i in sample_indices]

    st.markdown("### Public comparision of selected positions:")
    st.table(comparison_table)

    discrepancies = detect_eavesdropper(st.session_state["alice_bits"], st.session_state["bob_results"], sample_indices)
    st.session_state["eve_committed"] = True

    st.markdown("### 🗝️ Final Shared Key")
    key_string = "".join(str(bit) for bit in shared_key)
    st.code(key_string)

    if discrepancies:
        st.warning(f"⚠️ Discrepancies detected at indices: {discrepancies}. Eve likely interfered. This key is NOT secure.")
    else:
        st.success("✅ No discrepancies found. The key is secure and can be used for encryption.")

