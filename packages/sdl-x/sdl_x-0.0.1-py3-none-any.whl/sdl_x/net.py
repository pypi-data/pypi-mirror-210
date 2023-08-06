import numpy as np
from sdl_x import softmax
from sdl_x import cross_entropy_error
from sdl_x import numerical_gradient
from sdl_x.layers import Affine
from sdl_x.layers import Relu
from sdl_x.layers import SoftmaxWithLoss
from collections import OrderedDict
from sdl_x import active


class SimpleNet:
    def __init__(self):
        self.W = np.random.randn(2, 3)

    def predict(self, x):
        return np.dot(x, self.W)

    def loss(self, x, t):
        z = self.predict(x)
        y = softmax(z)
        loss = cross_entropy_error(y, t)

        return loss


class MultiLayerNet:
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        """多层网络
        这里，我们写死激活函数和输出函数以及lose函数。在需要的时候可以改动
        没有进行测试
        @:param
        hidden_size 为一个数组，中间层的输出个数
        """
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.weight_init_std = weight_init_std
        self.params = {}
        self.layers = OrderedDict()
        self._loop_net(self._create_net)
        self.lastLayer = SoftmaxWithLoss()

    def _loop_net(self, func):
        """除了最后的激活函数（输出函数），遍历所有的层
        func: 遍历用到的函数。参数：第几层，输入大小，输出大小，是否是最后的激活层"""
        index = 0
        input_size = self.input_size
        for index in range(0, len(self.hidden_size)):
            output_size = self.hidden_size[index]
            func(index, input_size, output_size, False)
            input_size = output_size
        func(index + 1, input_size, self.output_size, True)

    def _create_net(self, index, input_size, output_size, is_last):
        W_index = 'W{}'.format(index)
        b_index = 'b{}'.format(index)
        self.params[W_index] = self.weight_init_std * np.random.randn(input_size, output_size)
        self.params[b_index] = np.zeros(output_size)
        self.layers['Affine{}'.format(index)] = Affine(self.params[W_index], self.params[b_index])
        if not is_last:
            self.layers['Relu{}'.format(index)] = Relu()

    def predict(self, x):
        for layer in self.layers.values():
            x = layer.forward(x)
        return x

    def loss(self, x, t):
        y = self.predict(x)
        return self.lastLayer.forward(y, t)

    def accuracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)
        accuracy = np.sum(y == t) / float(x.shape[0])
        return accuracy

    def _calc_numerical_gradient(self, index, grads, x, t):
        loss_func = lambda W: self.loss(x, t)
        W_index = 'W{}'.format(index)
        b_index = 'b{}'.format(index)

        grads[W_index] = numerical_gradient(loss_func, self.params[W_index])
        grads[b_index] = numerical_gradient(loss_func, self.params[b_index])

    def numerical_gradient(self, x, t):
        grads = {}
        self._loop_net(lambda index, input_size, output_size, is_last: self._calc_numerical_gradient(index, grads, x, t))
        return grads

    def _calc_gradient(self, index, grads):
        grads['W{}'.format(index)] = self.layers['Affine{}'.format(index)].dW
        grads['b{}'.format(index)] = self.layers['Affine{}'.format(index)].db

    def gradient(self, x, t):
        # forward
        self.loss(x, t)

        # backward
        dout = 1
        dout = self.lastLayer.backward(dout)

        layers = list(self.layers.values())
        layers.reverse()
        for layer in layers:
            dout = layer.backward(dout)

        grads = {}
        self._loop_net(lambda index, input_size, output_size, is_last: \
                           self._calc_gradient(index, grads))

        return grads


class TwoLayerNet(MultiLayerNet):
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        MultiLayerNet.__init__(self, input_size, [hidden_size], output_size, weight_init_std)


class TwoLayerNet_OLD:
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        self.params = {'W1': weight_init_std * \
                             np.random.randn(input_size, hidden_size), 'b1': np.zeros(hidden_size),
                       'W2': weight_init_std * \
                             np.random.randn(hidden_size, output_size), 'b2': np.zeros(output_size)}

        # 生成层
        self.layers = OrderedDict()
        self.layers['Affine1'] = Affine(self.params['W1'], self.params['b1'])
        self.layers['Relu1'] = Relu()
        self.layers['Affine2'] = Affine(self.params['W2'], self.params['b2'])

        self.lastLayer = SoftmaxWithLoss()

    def predict(self, x):
        for layer in self.layers.values():
            x = layer.forward(x)
        return x

    def loss(self, x, t):
        y = self.predict(x)
        return self.lastLayer.forward(y, t)

    def accuracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)
        accuracy = np.sum(y == t) / float(x.shape[0])
        return accuracy

    def numerical_gradient(self, x, t):
        loss_func = lambda W: self.loss(x, t)

        grads = {'W1': numerical_gradient(loss_func, self.params['W1']),
                 'b1': numerical_gradient(loss_func, self.params['b1']),
                 'W2': numerical_gradient(loss_func, self.params['W2']),
                 'b2': numerical_gradient(loss_func, self.params['b2'])}
        return grads

    def gradient(self, x, t):
        # forward
        self.loss(x, t)

        # backward
        dout = 1
        dout = self.lastLayer.backward(dout)

        layers = list(self.layers.values())
        layers.reverse()
        for layer in layers:
            dout = layer.backward(dout)

        grads = {'W1': self.layers['Affine1'].dW,
                 'b1': self.layers['Affine1'].db,
                 'W2': self.layers['Affine2'].dW,
                 'b2': self.layers['Affine2'].db}
        return grads



class SimpleTwoLayerNet():
    """只用到基本概念的net"""

    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        self.params = {'W1': weight_init_std * \
                             np.random.randn(input_size, hidden_size),
                       'b1': np.zeros(hidden_size),
                       'W2': weight_init_std * \
                             np.random.randn(hidden_size, output_size),
                       'b2': np.zeros(output_size)}

    def predict(self, x):
        W1, W2 = self.params['W1'], self.params['W2']
        b1, b2 = self.params['b1'], self.params['b2']

        a1 = np.dot(x, W1) + b1
        z1 = active.sigmoid(a1)
        a2 = np.dot(z1, W2) + b2
        y = active.softmax(a2)

        return y

    def loss(self, x, t):
        y = self.predict(x)
        return cross_entropy_error(y, t)

    def accuracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)
        accuracy = np.sum(y == t) / float(x.shape[0])
        return accuracy

    def numerical_gradient(self, x, t):
        loss_func = lambda W: self.loss(x, t)

        grads = {'W1': numerical_gradient(loss_func, self.params['W1']),
                 'b1': numerical_gradient(loss_func, self.params['b1']),
                 'W2': numerical_gradient(loss_func, self.params['W2']),
                 'b2': numerical_gradient(loss_func, self.params['b2'])}
        return grads
