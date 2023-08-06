import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_digits
from sklearn.utils import shuffle


def init_param():
    scale = 0.1
    w1 = np.random.normal(0, scale, (10, 64))
    b1 = np.random.normal(0, scale, (10, 1))
    w2 = np.random.normal(0, scale, (10, 10))
    b2 = np.random.normal(0, scale, (10, 1))
    return w1, b1, w2, b2


def ReLU(z):
    return np.maximum(0, z)


def dReLU(z):
    return z > 0


def sigmoid(z):
    return 1 / (1 + np.exp(-z))
    # return np.exp(z) / np.sum(np.exp(z))


def dsigmoid(z):
    return sigmoid(z) * (1 - sigmoid(z))


def forward_prop(w1, b1, w2, b2, x):
    z1 = w1.dot(x).reshape(-1, 1) + b1
    # print(z1.max(), z1.min())
    a1 = ReLU(z1)
    z2 = w2.dot(a1) + b2
    a2 = sigmoid(z2)
    return z1, a1, z2, a2


def one_hot(y):
    one_hot_y = np.zeros((y.size, 10))
    one_hot_y[np.arange(y.size), y] = 1
    return one_hot_y.T


def back_prop(z1, a1, z2, a2, w2, x, y):
    one_hot_y = one_hot(y)

    dz2 = 2*(a2 - one_hot_y) * dsigmoid(z2)
    # print('d', dz2.max(), dz2.min())
    dw2 = dz2.dot(a1.T)
    db2 = np.sum(dz2, 1, keepdims=True)

    dz1 = w2.T.dot(dz2) * dReLU(z1)
    dw1 = dz1.dot(x.T)
    db1 = np.sum(dz1, 1, keepdims=True)

    return dw1, db1, dw2, db2


def update_param(w1, b1, w2, b2, dw1, db1, dw2, db2, lr):
    w1 = w1 - lr*dw1
    b1 = b1 - lr*db1
    w2 = w2 - lr*dw2
    b2 = b2 - lr*db2
    return w1, b1, w2, b2


def gradient_descent(X, Y, max_iter, lr):
    w1, b1, w2, b2 = init_param()
    m = len(X)
    for _ in range(max_iter):
        y_hat = []
        dw1, db1, dw2, db2 = np.zeros_like(w1), np.zeros_like(
            b1), np.zeros_like(w2), np.zeros_like(b2)
        for x, y in zip(X, Y):
            x = x.reshape(-1, 1)
            z1, a1, z2, a2 = forward_prop(w1, b1, w2, b2, x)
            _dw1, _db1, _dw2, _db2 = back_prop(z1, a1, z2, a2, w2, x, y)
            dw1 += _dw1
            db1 += _db1
            dw2 += _dw2
            db2 += _db2
            # print(a2.max(), a2.min(), np.argmax(a2))
            y_hat.append(np.argmax(a2))
        w1, b1, w2, b2 = update_param(
            w1, b1, w2, b2, dw1, db1, dw2, db2, lr*(1/m))
        print(accuracy_score(Y, y_hat))
    return w1, b1, w2, b2


if __name__ == '__main__':
    mnist = load_digits(n_class=10)
    # X = np.random.rand(8, 64)
    # Y = np.floor(X.sum(axis=-1).reshape((-1, 1)) / 6.4).astype(np.int32)

    mnist.data, mnist.target = shuffle(mnist.data, mnist.target)
    data, labels = mnist.data, mnist.target
    data = data / data.max()

    Xtrain, Xvalid, Xtest = data[:1000], data[1000:2000], data[2000:]
    Ytrain, Yvalid, Ytest = labels[:1000], labels[1000:2000], labels[2000:]

    gradient_descent(Xtrain,
                     Ytrain, 1000, 0.5)

# Should use dtanh instead of tanh
# Should initialise smaller weights (vanishing gradients)
# Need to define a loss function
# Tanh isn't a great activation function for
