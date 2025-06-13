from bb84 import generate_alice_data, generate_bob_bases
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
        bob_bases = generate_bob_bases(n)
        st.session_state["bob_bases"] = bob_bases.tolist()
        
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