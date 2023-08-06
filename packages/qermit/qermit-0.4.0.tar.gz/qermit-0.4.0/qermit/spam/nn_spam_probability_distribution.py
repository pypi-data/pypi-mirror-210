import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
from pytket.backends.backendresult import BackendResult
from pytket.extensions.qiskit import AerBackend
from pytket import Circuit
import math
import matplotlib.pyplot as plt

small = 0.000001


def int_to_bin(i: int) -> list[int]:
    b = []
    while i > 0:
        b.insert(0, i % 2)
        i //= 2
    assert len(b) <= n_qubits
    while len(b) < n_qubits:
        b.insert(0, 0)
    return tuple(b)


def bin_to_int(b: list[int]) -> int:
    i = 0
    while len(b) > 0:
        i = 2 * i + b.pop(0)
    return i


def distribution_to_vector(distribution: dict):
    v = []
    for i in range(2 ** n_qubits):
        if int_to_bin(i) in distribution.keys():
            v.append(distribution[int_to_bin(i)])
        else:
            v.append(0)
    return np.array(v)


def cross_entropy(distribution_one, distribution_two):
    return -sum(
        prob_one * math.log2(max(prob_two, small))
        for prob_one, prob_two in zip(distribution_one, distribution_two)
    )


class SPAMProbDistNN(keras.Sequential):
    def __init__(self, n_qubits: int):

        super().__init__()

        self.n_qubits = n_qubits

        self.add(keras.Input(shape=(2 ** self.n_qubits)))
        self.add(layers.Dense(400, activation="relu"))
        self.add(layers.Dropout(0.2))
        self.add(layers.Dense(200, activation="relu"))
        self.add(layers.Dense(2 ** self.n_qubits, activation="softmax"))

        self.compile(optimizer="adam", loss="kld")
        self.summary()

    def format_results(self, result_list):

        return np.array(
            [
                distribution_to_vector(result.get_distribution())
                for result in result_list
            ]
        )

    def format_binary(self, binary_data):

        training_y_data = np.array([np.zeros(2 ** n_qubits) for _ in binary_data])
        for i, b in enumerate(binary_data):
            training_y_data[i][bin_to_int(list(b))] = 1
        return training_y_data


result_dir = "manila_emulator"
n_qubits = 5
n_training = 280
n_testing = 20
max_shots = 100000

spam_nn = SPAMProbDistNN(n_qubits)

with open(f"{result_dir}/result_list.json", "r") as fp:
    json_result_list = json.load(fp)
result_list = np.array(
    [BackendResult().from_dict(json_result) for json_result in json_result_list]
)

with open(f"{result_dir}/binary_string_list.json", "r") as fp:
    binary_data = json.load(fp)
binary_data = np.array(binary_data)

training_result_list = result_list[:n_training]
training_binary_data = binary_data

training_x_data = spam_nn.format_results(training_result_list)
training_y_data = spam_nn.format_binary(training_binary_data)

callbacks = [keras.callbacks.TensorBoard(log_dir="./logs")]
history = spam_nn.fit(
    training_x_data, training_y_data, batch_size=40, epochs=50, callbacks=callbacks
)

evaluation = spam_nn.evaluate(training_x_data[:10], training_y_data[:10])
print("evaluation", evaluation)

cross_entropy_measured = []
cross_entropy_learnt = []
processed_data = spam_nn(training_x_data[:10])
for measured, learnt, correct in zip(
    training_x_data[:10], processed_data, training_y_data[:10]
):
    print(
        "=============================",
        "learnt",
        learnt,
        "measured",
        measured,
        "correct",
        correct,
        sep="\n",
    )
    print("measured cross entropy", cross_entropy(measured, correct))
    cross_entropy_measured.append(cross_entropy(measured, correct))
    print("learnt cross entropy", cross_entropy(learnt.numpy(), correct))
    cross_entropy_learnt.append(cross_entropy(learnt.numpy(), correct))

plt.bar(
    x=[i + 0.1 for i in range(10)],
    height=cross_entropy_measured,
    width=0.2,
    label="Measured",
)
plt.bar(
    x=[i - 0.1 for i in range(10)],
    height=cross_entropy_learnt,
    width=0.2,
    label="Learnt",
)
plt.show()

with open(f"{result_dir}/circ_list.json", "r") as fp:
    json_circ_list = json.load(fp)
circ_list = [Circuit().from_dict(circ_dict) for circ_dict in json_circ_list]
circ_list = circ_list[n_training:]

testing_ideal_result_list = AerBackend().run_circuits(circ_list, n_shots=max_shots)
testing_y_data = spam_nn.format_results(testing_ideal_result_list)

testing_real_result_list = result_list[n_training:]
testing_x_data = spam_nn.format_results(testing_real_result_list)

evaluation = spam_nn.evaluate(testing_x_data, testing_y_data)
print("evaluation", evaluation)

cross_entropy_measured = []
cross_entropy_learnt = []
processed_data = spam_nn(testing_x_data)
for measured, learnt, correct in zip(testing_x_data, processed_data, testing_y_data):
    print(
        "=============================",
        "learnt",
        learnt,
        "measured",
        measured,
        "correct",
        correct,
        sep="\n",
    )
    print("measured cross entropy", cross_entropy(measured, correct))
    cross_entropy_measured.append(cross_entropy(measured, correct))
    print("learnt cross entropy", cross_entropy(learnt.numpy(), correct))
    cross_entropy_learnt.append(cross_entropy(learnt.numpy(), correct))

plt.bar(
    x=[i + 0.1 for i in range(20)],
    height=cross_entropy_measured,
    width=0.2,
    label="Measured",
)
plt.bar(
    x=[i - 0.1 for i in range(20)],
    height=cross_entropy_learnt,
    width=0.2,
    label="Learnt",
)
plt.show()
