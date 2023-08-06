import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
from pytket.backends.backendresult import BackendResult


class SPAMNN:
    def __init__(self, n_qubits: int):

        self.n_qubits = n_qubits

        self.model = keras.Sequential()
        self.model.add(keras.Input(shape=(self.n_qubits), dtype=tf.int32))
        self.model.add(layers.Dense(400, activation="relu"))
        self.model.add(layers.Dropout(0.2))
        self.model.add(layers.Dense(200, activation="relu"))
        self.model.add(layers.Dense(self.n_qubits, activation="sigmoid"))

        self.model.compile(optimizer="adam", loss="binary_crossentropy")
        self.model.summary()


result_dir = "ibmq_manila_emulator_data"
n_qubits = 5
n_training = 100000
n_testing = 20

with open(f"{result_dir}/result_list.json", "r") as fp:
    json_result_list = json.load(fp)
result_list = [
    BackendResult().from_dict(json_result) for json_result in json_result_list
]
training_x_data = np.array([result.get_shots() for result in result_list])

with open(f"{result_dir}/training_y_data.json", "r") as fp:
    training_y_data = json.load(fp)
training_y_data = np.array(
    [
        [y_data for _ in x_data]
        for y_data, x_data in zip(training_y_data, training_x_data)
    ]
)

shape = training_x_data.shape
assert training_y_data.shape == shape
flattened_shape = (shape[0] * shape[1], shape[2])

training_x_data = np.reshape(training_x_data, flattened_shape)
training_y_data = np.reshape(training_y_data, flattened_shape)

idx = np.random.choice(flattened_shape[0], n_training + n_testing, replace=False)

testing_x_data = training_x_data[idx[:n_testing], :]
training_x_data = training_x_data[idx[n_testing:], :]

testing_y_data = training_y_data[idx[:n_testing], :]
training_y_data = training_y_data[idx[n_testing:], :]

n_qubits = flattened_shape[1]
spam_nn = SPAMNN(n_qubits)

callbacks = [keras.callbacks.TensorBoard(log_dir="./logs")]
history = spam_nn.model.fit(
    training_x_data, training_y_data, batch_size=1000, epochs=3, callbacks=callbacks
)
print("history", history.history)

evaluation = spam_nn.model.evaluate(testing_x_data, testing_y_data)
print("evaluation", evaluation)

processed_data = spam_nn.model(testing_x_data)
for measured, learnt, correct in zip(testing_x_data, processed_data, testing_y_data):
    print("learnt", learnt, "measured", measured, "correct", correct)
