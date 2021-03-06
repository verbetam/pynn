"""utils.py
~~~~~~~~~~~

Contains the base methods for neural networks which are universal to all neural
networks. Activation and Cost functions should be declared in their independent
class as static methods. If a contained activation or cost function does fit the
intended use case, then a custom class may be declared and passed to the Network
class to be used instead.

Micheal Nielsen's book on neural networks has been very helpful with this
project, and I have used his code many times to see how to address problems.
https://github.com/mnielsen/neural-networks-and-deep-learning

General Notation:
    x: Input
    z: Weighted input (tx+b)
    a: Output (activation), sigma(z)
    y: Desired output for related x in the training set
    Sigma: Activation function, or class wrapper
    Theta: Weights of the network, parametrizing H() and J()
    Nabla: Gradient of a function (e.g, nabla_t is the gradient of J() in terms
    of theta)
    J: The cost function of the network
    H: The hypothesis function of the network
    Prime: A derivative function. E.g, sigma.prime
    Delta: The value of a derivative function. I.e, delta = sigma.prime(z), but
    not sigma.delta

"""

"""Standard Libraries"""
import random

"""Third-party Libraries"""
import numpy as np

# Misc functions
def z(theta, x, bias):
    """Computes the weighted input
     Takes a list of weights ``theta`` and a list of inputs ``x`` and returns
     a list of weighted inputs with the given list of biases ``bias`` as ``w*x+b``.
    """
    return np.dot(theta, x) + bias

def bernoulli(layers, p):
    """Computes and returns a numpy array for use in dropout, creating an 2d
    array where each row represents a layer in the network with a either a 0 or a
    1. The output layer will always be a row of ones. ``layers`` is the nets
    ``layers`` internal variable and ``p`` is the inverse probability of each
    neuron being dropped, a value between 0 and 1.
    """
    bs = [[np.random.binomial(1, p) for n in xrange(l)] for l in layers[:-1]]
    bs.append([1]*layers[-1])
    return bs


# Activation classes
# Required Functions:
#   fn(z) returns the activation value for weighted input z
#   prime(z) returns the derivative of the activation function for weighted
#   input z.
class LinearActivation:
    """Class containing methods for linear regression activation
    For predicting a continual value, without classification."""

    @staticmethod
    def fn(z):
        """Linear regression activation, unmodified output"""
        return z

    @staticmethod
    def prime(z):
        """Linear regression activation derivative"""
        return 1

class SigmoidActivation:
    """Class containing methods for sigmoid activation.
    For classification, returns a value between 0 and 1."""

    @staticmethod
    def fn(z):
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-z))

    @staticmethod
    def prime(z):
        """Sigmoid activation function derivative"""
        return fn(z) * (1 - fn(z))

class TanhActivation:
    """Class containing methods for tanch activation.
    For classification, returns a value between -1 and 1."""

    @staticmethod
    def fn(z):
        """Tanh activation function"""
        return (np.exp(z) - np.exp(-z)) / (np.exp(z) + np.exp(-z))

    @staticmethod
    def prime(z):
        """Tanh activation function derivative"""
        return 1 - ((np.exp(z) - np.exp(-z))**2 / (np.exp(z) + np.exp(-z))**2)

class ReLUActivation:
    """Class containing method for ReLU activation.
    For classification, returns a value >= 0. Rectified linear.
    """

    @staticmethod
    def fn(z):
        """ReLU activation function"""
        return 0 if z <= 0 else z

    @staticmethod
    def prime(z):
        """ReLU activation function derivative"""
        return z if z <= 0 else 1

# Note: Due to the fact that the PReLU activation adds another parameter that
# will be learned, it is not directly supported by the library as of yet. Extra
# steps must be taken to use it.
# TODO: Generalize to allow PReLU
class PReLUActivation:
    """Class containing methods for PReLU activation.
    For classification, returns any real number. Parametric Rectified Linear.
    """

    @staticmethod
    def fn(z, a):
        """PReLU activation function"""
        return a * z if z <= 0 else z

    def prime(z, a):
        """PReLU activation function derivative"""
        return a if z <= 0 else 1


# Cost classes
# Required Functions:
#   fn(a, y) returns the cost for output a and desired output y.
#   grad(theta, a, x, y) returned the gradient for the cost function. theta is
#   the weights of the network parameterizing sigma.fn() (J()), a is the output
#   of the network for input x, and y is the desired output for input x.
class SquaredErrorCost:
    """Class containing methods for squared error cost calculation"""

    @staticmethod
    def fn(a, y):
        """Calculates the squares error cost for output ``a`` and desired output ``y``"""
        return 0.5 * np.linalg.norm(a - y)**2

    @staticmethod
    def prime(a, y):
        """Computes the derivative of the squared error cost function for output
        ``a`` and desired output ``y``."""
        return a - y

class CrossEntropyCost:
    """Class containing methods for cross entropy cost calculation"""

    @staticmethod
    def fn(a, y):
        """Calculates the cross entropy cost for output ``a`` and desired
        output ``y``."""
        return np.sum(np.nan_to_num(-y*np.log(a) - (1 - y) * np.log(1 - a)))

    @staticmethod
    def prime(a, y):
        """Computes the cross entropy cost derivative for output ``a`` and
        desired output ``y``."""
        return (a - y)


#Training classes
class SGD:
    """Class containing methods for the stochastic gradient descent training
    technique."""

    def train(net, trainingData, epochs, batchSize, alpha,
              lmbda   = 0.0,
              mu      = 0.0,
              p       = 1.0,
              verbose = False):
        """Train the neural network using mini-batch stochastic gradient
        descent.  The ``trainingData`` is a list of tuples ``(x, y)``
        representing the training inputs and the desired outputs.  ``epochs`` is
        the number of training iterations through ``trainingData``.
        ``batchSize`` is the size of each batch. ``alpha`` is the learning
        rate, ``lmbda`` is the weight decay regularization parameter. ``mu`` is
        the momentum coefficient. ``p`` is the dropout porabability.
        ``verbose`` determines whether the completion of each epoch is posted."""
        n = len(trainingData)
        # Shuffle data and train on each minibatch for each epoch
        for epoch in xrange(epochs):
            random.shuffle(trainingData)
            mini_batches = [
                trainingData[i:i+batchSize]
                for i in xrange(0, n, batchSize)]
            v = 0.0
            for mini_batch in mini_batches:
                v = bath_gradient_descent(net, mini_batch, alpha, lmbda, mu, v)
            if verbose:
                print "Epoch %s training complete\n" % i

    def batch_gradient_descent(net, batch, alpha, lmbda, mu, p, v):
        """Executes on iteration of batch gradient descent. ``batch`` is the
        the mini batch as a list of tuples in the form ``(x, y)``, ``alpha``
        is the learning rate, ``lmbda`` is the regularization parameter, and
        ``n`` is the total training set length. ``mu`` is the momentum and ``v``
        the velocity, in other words, the previous ``delta_t``. ``p`` is the
        dropout porabability.

        The method returns ``v`` for storing sotring it as the velocity for
        momentum descent. Essentially, the method returns the value to be passed
        as ``v`` on the next call, with an initial call of ``v`` = 0.
        """
        delta_t = [np.zeros(b.shape) for b in net.biases]
        delta_b = [np.zeros(w.shape) for t in net.theta]
        ber = bernoulli(net.layers, p)
        for x, y in batch:
            nabla_t, nabla_b = backprop(net, x, y, mu, v, ber)
            delta_t = delta_t + np.multiply(ber[1:], nabla_t)
            delta_b = delta_b + np.multiply(ber[1:], nabla_b)
        # t(l) = t(l) - alpha[(delta_t(l)/m) + lmbda * t(l)]
        v = np.multiply(mu, v) + np.multiply(alpha,
            np.multiply(delta_t, 1 / len(batch)) + np.multiply(lmbda,
            net.theta))
        net.theta = net.theta - v
        #b(l) = b(l) - alpha[delta_b(l)/m]
        net.biases = net.biases - np.multiply(alpha,
            np.multiply(delta_b, 1 / len(batch)))
        return v

    def backprop(net, x, y, mu, v, ber):
        """Returns a tuple containing the gradient for the network's cost
        function in terms of theta and bias based on input ``x`` and desired
        output ``y`` as ``(nabla_t, nabla_b)``. ``mu`` is the momentum
        coefficient of the descent and ``v`` is the velocity. ``mu`` and ``v``
        are needed to compute the Nesterov Accelerated Gradient. ``ber`` is a
        bernoulli distribution as an 2d-array with reach row representing the
        status of the noded by layer.
        """
        nabla_t = [np.zeros(w.shape) for t in net.theta]
        nabla_b = [np.zeros(b.shape) for b in net.biases]
        # Preform a forward pass through the network and store the needed results
        # into arrays for the back propagation step.
        a  = np.multiply(ber[1], x) # The activation of the previous layer
        al = [a]                    # By layer activation, including input layer
        zl = [ ]                    # By layer weighted inputs, skipping input layer
        for b, t in zip(net.biases, np.multiply(ber[1:], net.theta +
            np.multiply(mu, v))):
            z = z(t, a, b)
            a = net.sigmaVec(z)
            zl.append(z)
            al.append(a)
        # Preform a back propagation
        delta = np.multiply(net.costPrimeVec(a, y), net.sigmaPrimeVec(zl[-1]))
        nabla_t[-1] = np.dot(delta, np.transpose(al[-2]))
        nable_b[-1] = delta
        for l in xrange(2, net.nl):
            delta = np.multiply(np.dot(np.transpose(np.multiply(ber[-l],
                net.thata[-l])), delta),
                net.sigmaPrimeVec(zl[-l]))
            nabla_b[-l] = delta
            nabla_t[-l] = np.dot(delta, np.transpose(al[-l]))
        return (nabla_t, babla_b)
