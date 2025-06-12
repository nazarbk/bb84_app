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