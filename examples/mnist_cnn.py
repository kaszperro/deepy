from time import time

import numpy as np

from slick_dnn.autograd.activations import Softmax, ReLU
from slick_dnn.autograd.losses import CrossEntropyLoss
from slick_dnn.optimizers import Adam
from slick_dnn.autograd.tensor_modifications import MaxPool2d, Flatten
from slick_dnn.data import DataLoader
from slick_dnn.data.example_datasets import MNISTTrainDataSet, MNISTTestDataSet
from slick_dnn.module import Linear, Sequential, Conv2d
from slick_dnn.variable import Variable

batch_size = 64
iterations = 10
learning_rate = 0.0002

my_model = Sequential(
    Conv2d(input_channels=1, output_channels=20, kernel_size=5, stride=1),
    ReLU(),
    MaxPool2d(2, 2),
    Conv2d(input_channels=20, output_channels=50, kernel_size=5, stride=1),
    ReLU(),
    MaxPool2d(kernel_size=2, stride=2),
    Flatten(),
    Linear(800, 500),
    ReLU(),
    Linear(500, 10),
    Softmax()
)

train_dataset = MNISTTrainDataSet(flatten_input=False, one_hot_output=True, input_normalization=(0.1307, 0.3081))
test_dataset = MNISTTestDataSet(flatten_input=False, one_hot_output=True, input_normalization=(0.1307, 0.3081))

train_data_loader = DataLoader(train_dataset)
test_data_loader = DataLoader(test_dataset)

train_batches = train_data_loader.get_batch_iterable(batch_size)
test_batches = test_data_loader.get_batch_iterable(batch_size)

optimizer = Adam(my_model.get_variables_list(), learning_rate)

loss = CrossEntropyLoss()

single_iter = test_data_loader.get_single_iterable()


def test_model_acc():
    correct = 0
    for test_batch_in, test_batch_out in test_batches:
        test_output = my_model(Variable(test_batch_in)).data
        correct += np.sum(np.argmax(test_output, axis=1) == np.argmax(test_batch_out, axis=1))

    my_acc = correct / len(test_dataset)
    return my_acc


finished = False
for it in range(iterations):
    if finished:
        break
    train_batches.shuffle()
    start = time()
    for i_b, (batch_in, batch_out) in enumerate(train_batches):
        model_input = Variable(batch_in)
        good_output = Variable(batch_out)
        model_output = my_model(model_input)

        err = loss(good_output, model_output)

        optimizer.zero_grad()
        err.backward()
        optimizer.step()

        if i_b % 100 == 0:
            print(i_b)

    print("epoch time: {:.2f} seconds".format(time() - start))
    acc = test_model_acc()
    print("model accuracy: {}".format(acc))
    if acc > 0.99:
        finished = True
        break
