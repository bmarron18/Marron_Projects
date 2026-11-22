# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 21:28:42 2016

@author: bmarron
"""
#%%

http://stackoverflow.com/questions/31602200/full-matrix-approach-to-backpropagation-in-artificial-neural-network

#%%
def feedforward2(self, a):
    zs = []
    activations = [a]

    activation = a
    for b, w in zip(self.biases, self.weights):
        z = np.dot(w, activation) + b
        zs.append(z)
        activation = sigmoid(z)
        activations.append(activation)

    return (zs, activations)

def update_mini_batch2(self, mini_batch, eta):
    batch_size = len(mini_batch)

    # transform to (input x batch_size) matrix
    x = np.asarray([_x.ravel() for _x, _y in mini_batch]).transpose()
    # transform to (output x batch_size) matrix
    y = np.asarray([_y.ravel() for _x, _y in mini_batch]).transpose()

    nabla_b, nabla_w = self.backprop2(x, y)
    self.weights = [w - (eta / batch_size) * nw for w, nw in zip(self.weights, nabla_w)]
    self.biases = [b - (eta / batch_size) * nb for b, nb in zip(self.biases, nabla_b)]

    return

def backprop2(self, x, y):

    nabla_b = [0 for i in self.biases]
    nabla_w = [0 for i in self.weights]

    # feedforward
    zs, activations = self.feedforward2(x)

    # backward pass
    delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
    nabla_b[-1] = delta.sum(1).reshape([len(delta), 1]) # reshape to (n x 1) matrix
    nabla_w[-1] = np.dot(delta, activations[-2].transpose())

    for l in xrange(2, self.num_layers):
        z = zs[-l]
        sp = sigmoid_prime(z)
        delta = np.dot(self.weights[-l + 1].transpose(), delta) * sp
        nabla_b[-l] = delta.sum(1).reshape([len(delta), 1]) # reshape to (n x 1) matrix
        nabla_w[-l] = np.dot(delta, activations[-l - 1].transpose())

    return (nabla_b, nabla_w)