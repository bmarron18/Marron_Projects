# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 08:00:20 2016
from development model Marron_Hwk2_NN5.py
@author: bmarron
""""

#%%Required pkgs (imports)
import random
import cPickle
import string
import pandas as pd
import numpy as np


#processed training data
tr_d=cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk2/DataFiles/Input_Data/Processed/tr_d/tr_d.pkl","rb"))

#processed test data
te_d=cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk2/DataFiles/Input_Data/Processed/te_d/te_d.pkl","rb"))


#%% The Neural Network (w/0 momentum)

    #NN layers
NNsize=[16,4,26]
np.random.seed(47)
 

#define the activation fxn (sigmoid)
 #define the derivative of the activation fxn (sigmoid_prime)
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
        
#        self.nabla_btp = [np.zeros(b.shape) for b in self.biases]
#        self.nabla_wtp = [np.zeros(w.shape) for w in self.weights]



    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a)+b)
        return a


          
    def SGD(self, tr_d, epochs, eta, te_d=None):
        if te_d:
            n_te_d = len(te_d)        
        for j in xrange(epochs):
            for k in xrange(len(tr_d)):
                self.update_perdatum(tr_d[k], eta)
            if te_d:
                print "Epoch {0}: {1} / {2}".format(j, self.evaluate(te_d), n_te_d)
            else:
                print "Epoch {0} complete".format(j)
                

    def update_perdatum(self, datum, eta):
        x=datum[0]
        y=datum[1]
        nabla_b, nabla_w = self.backprop(x, y)        
        self.weights = [w+((eta)*nw) for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b+((eta)*nb) for b, nb in zip(self.biases, nabla_b)]
#        self.nabla_btp=nabla_b
#        self.nabla_wtp=nabla_w

#(1) nabla_a creates an array  [[4x1], [26x1]] of zeros. b retains its
#last value from the loop (i.e., self.biases[1])
#(2) nabla_w creates an array  [[4x16], [26x4]] of zeros. w retains its
#last value from the loop (i.e., self.weights[1]) 

#nabla_b[0] == biases on hidden nodes
#nabla_b[0].shape = (hidden nodes x1)
#nabla_b[1] == biases on output nodes
#nabla_b[1].shape =(output nodesx1)

#nabla_w[0] == wgts between input-hidden nodes
#nabla_w[0].shape = (hidden nodes x input nodes)
#nabla_w[1] == wgts between hidden-output nodes
#nabla_w[1].shape =(output nodes x input nodes)

#x = input from tr_d[i][0]
#y = input from tr_d[i][1]  for i= 0 to 9999

# (1) delta_error == the derivative of the error function with respect to the 
#neuron's inputs. Neglecting the multiplicative constant (=2)
#(2) nabla_b[-1].shape = (26 x 1)
#(3) nabla_w[-1].shape  = (26 x 16)

    def backprop(self, x, y):
      
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        
# forward propagation        
# 
#x == activation from L1 nodes (ie, tr_d[0][0], tr_d[1][0], etc) 
        a_L1 = x  
        a_values = [x]
        z_values = [] 

        z_L2 = np.dot(self.weights[0], a_L1) + self.biases[0]
        z_values.append(z_L2)  #(4 x 1)
        a_L2 = sigmoid(z_L2)
        a_values.append(a_L2)

        z_L3 = np.dot(self.weights[1], a_L2) + self.biases[1]
        z_values.append(z_L3)
        a_L3 = sigmoid(z_L3)
        a_values.append(a_L3)


# backward propagation
#(1) del_error == the derivative of the error function with respect to the 
#neuron's inputs. Neglect multiplicative constant (=2)
#(2) nabla_b[-1].shape = (26 x 1)
#(3) nabla_w[-1].shape  = (26 x 16)
        del_error_L3 = self.error(a_values[-1], y) * sigmoid_prime(z_values[-1])
        nabla_b[-1] = del_error_L3
        nabla_w[-1] = np.dot(del_error_L3, a_values[-2].T)

        del_error_L2 = np.dot(self.weights[-1].T, del_error_L3) * sigmoid_prime(z_values[-2])
        nabla_b[-2] = del_error_L2
        nabla_w[-2] = np.dot(del_error_L2, a_values[-3].T)
        return (nabla_b, nabla_w)
        
        
    def error(self, a_L3, y): 
        return (a_L3-y)  
        
        
    def evaluate(self, te_d):
        results=[]
        for i in xrange(0,len(te_d)):    
            x= np.argmax(self.feedforward(te_d[i][0]))
            y= np.argmax([te_d[i][1]])
            result = int(x==y)
            results.append(result)
        return sum(results)


        
