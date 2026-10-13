from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# 1. Crear un circuito cuántico de 2 qubits y 2 bits clásicos
qc = QuantumCircuit(2, 2)

# 2. Aplicar la puerta Hadamard al qubit 0 (crea superposición)
qc.h(0)

# 3. Aplicar la puerta CNOT con control en q0 y objetivo en q1 (crea entrelazamiento)
qc.cx(0, 1)

# 4. Medir ambos qubits y guardar los resultados en los bits clásicos
qc.measure([0, 1], [0, 1])

# --- Visualización del circuito ---
print("Diagrama del circuito cuántico:")
print(qc.draw(output='text'))

# --- Simulación del circuito ---
simulator = AerSimulator()
job = simulator.run(qc, shots=1000)  # Ejecutamos el circuito 1000 veces
result = job.result()
counts = result.get_counts()

print("\nResultados de la medición (1000 ejecuciones):")
print(counts)