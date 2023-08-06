from pytket.extensions.qiskit import IBMQEmulatorBackend, IBMQBackend
import random
from pytket import Circuit
import json
import numpy as np
from quantinuum_benchmarking.circuit_generation import RandomCircuit

backend = IBMQEmulatorBackend(
    backend_name="ibmq_manila", hub="partner-cqc", group="internal", project="default"
)
result_dir = "manila_emulator"
n_qubits = 5
num_train_circs = 280
num_test_circs = 20
assert num_train_circs + num_test_circs <= 300
max_shots = 100000

# Generate binary strings to ideally genereate
binary_string_list = [
    [random.getrandbits(1) for _ in range(n_qubits)] for _ in range(num_train_circs)
]
with open(f"{result_dir}/binary_string_list.json", "w") as fp:
    json.dump(binary_string_list, fp)

# Generate circuits corresponding to binary strings
circ_list = []
for binary_string in binary_string_list:
    circ = Circuit(n_qubits)
    for qubit, add_x in enumerate(binary_string):
        if add_x:
            circ.X(qubit)
    circ.measure_all()
    circ_list.append(circ)

# Genreate random training circuits
for _ in range(num_test_circs):
    circ = RandomCircuit(5, 2)
    circ.measure_all()
    compiled_circ = backend.get_compiled_circuit(circ)
    circ_list.append(compiled_circ)

# Save all circuits
json_circ_list = [circ.to_dict() for circ in circ_list]
with open(f"{result_dir}/circ_list.json", "w") as fp:
    json.dump(json_circ_list, fp)

# Submit circuits
result_handle_list = backend.process_circuits(
    circuits=circ_list, n_shots=[max_shots for _ in circ_list]
)
json_result_handle_list = [str(handle) for handle in result_handle_list]
with open(f"{result_dir}/result_handle_list.json", "w") as fp:
    json.dump(json_result_handle_list, fp)

# Retrieve results
result_list = backend.get_results(result_handle_list)
json_result_list = [result.to_dict() for result in result_list]
with open(f"{result_dir}/result_list.json", "w") as fp:
    json.dump(json_result_list, fp)
