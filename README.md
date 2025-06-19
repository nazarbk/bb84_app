# BB84 Protocol Simulation

This project is a **BB84 Protocol Simulator** built with Streamlit, Qiskit, and Matplotlib. It allows users to simulate the **Quantum Key Distribution (QKD)** protocol, generate a shared secret key between Alice and Bob, and detect the presence of an eavesdropper (Eve) interfering with the communication.

## 🚀 Features
- **Simulate the BB84 Protocol**: Generate random bits and bases for Alice, and let Bob measure with his bases (randomly or manually).
- **Eavesdropping detection**: Simulate Eve intercepting the qubits and potentially altering the transmission.
- **Shared key generation**: Alice and Bob compare their bases and bits, extracting a secure key.
- **Educational Explanations**: Each step of the process is explained interactively to help users understand quantum cryptography.

## 🧩 How to Run Locally

1. Clone this repository:
    ```bash
    git clone https://github.com/nazarbk/bb84_app
2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
4. Run the Streamlit app:
    ```bash
    cd app
    streamlit run app.py

This will launch the application in your browser, where you can interactively simulate the BB84 Protocol.

## 📌 How it works

1. **Step 1**: Alice generates a sequence of random bits (0 or 1) and encodes them into qubits using random bases (Z or X).
2. **Step 2**: Bob receives the qubits and measures them using his own bases (either randomly or manually).
3. **Step 3**: Alice and Bob compare their bases, and the bits where the bases match are kept to form the shared secret key.
4. **Step 4**: Alice and Bob publicly compare a few bits to detect discrepancies caused by Eve's interference. If discrepancies are found, the key is considered insecure.

- The **Quantum Circuit** is built using **Qiskit** and the statevector is computed.
- The **Bloch Sphere** visualization helps show how the quantum state evolves.
- **Measurement results** are disployed in a clean table for comparision.

## 📖 Educational Info

This simulation is designed to help users understand the inner workings of quantum cryptography. The help section explains each concept step by step.

## ✅ Credits
- Built by **Nazar Blanco**
- Powered by **Streamlit**, **Qiskit** and **Matplotlib**
- Based on the **BB84 Protocol** for Quantum Key Distribution (QKD)

## 📱 Contact
- [Nazar Blanco on LinkedIn](https://www.linkedin.com/in/nazar-blanco-kataran/)
- Check out my other project: [Quantum Single Qubit Visualizer](https://quantum-single-qubit-visualizer.streamlit.app/)
- Visit this project: [BB84 protocol]()