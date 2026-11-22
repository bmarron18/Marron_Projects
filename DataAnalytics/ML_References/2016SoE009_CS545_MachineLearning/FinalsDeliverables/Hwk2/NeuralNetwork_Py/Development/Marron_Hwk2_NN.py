# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 08:00:20 2016

@author: bmarron
""""

#%%Required pkgs (imports)
import random
import cPickle
import string
import pandas as pd
import numpy as np

#%%Load data

    #training data
tr_d=cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_work_inprogress/Hwk2/DataFiles/Processed/tr_d.pkl","rb"))


#%% The Neural Network

    #NN layers
NNsize=[16,4,26]
np.random.seed(47)
 
   #Cannot use scipy.special.expit here!!
    #define the activation fxn (sigmoid)
def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
    return sigmoid(z)*(1-sigmoid(z))       

    #define an initial conditions method with:
    #no. nodes/layer
    #random values between -.26, .26
    #biases hidden ==> output
    #must have after execution:
    #y = the no. neurons in output layer (=26)
    #x = the no. neurons in hidden layer (=5)
    #(1)Create an array  [[4x1], [26x1]] of random values between
    #-.26 and .26 for the biases. y retains its last value from the biases
    #loop (i.e., 26)
    #(2)Create an array  [[4x16], [26x4]] of random values between
    #-.26 and .26 for the weights. y retains its last value from the weights
    #loop (i.e., (4,26)
class NN(object):
    def __init__(self, NNsize):
        self.num_layers = len(NNsize)
        self.biases = [np.random.uniform(-.26, .26, y) for y in NNsize[1:]]
        self.biases[0] = self.biases[0].reshape((NNsize[1],1))
        self.biases[1] = self.biases[1].reshape((NNsize[2],1))  
        self.weights =[np.random.uniform(-.26, .26, y) for y in zip(NNsize[:-1], NNsize[1:])]
        self.weights[0] = self.weights[0].reshape(NNsize[1],NNsize[0])
        self.weights[1] = self.weights[1].reshape(NNsize[2],NNsize[1])
  
          
    def SGD(self, tr_d, epochs, eta, te_d=None):
        if te_d: n_te_d = len(te_d)        
        for j in xrange(epochs):
            for datum in tr_d:
                self.update_datum(datum, eta)
            if te_d:
                print "Epoch {0}: {1} / {2}".format(
                    j, self.evaluate(te_d), n_te_d)
            else:
                print "Epoch {0} complete".format(j)
                

    #(1) nabla_a creates an array  [[4x1], [26x1]] of zeros. b retains its
    #last value from the loop (i.e., self.biases[1])
    #(2) nabla_w creates an array  [[4x16], [26x4]] of zeros. w retains its
    #last value from the loop (i.e., self.weights[1]) 

    def update_datum(self, datum, eta):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        
        for x, y in datum:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta)*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta)*nb for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):        
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
            
        # backward pass
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
 
        for l in xrange(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, te_d): 
        test_results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in te_d]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y): 
        return (output_activations-y)  
        
