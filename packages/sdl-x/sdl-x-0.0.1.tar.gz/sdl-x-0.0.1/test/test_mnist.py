import sdl.mnist as mnist
import matplotlib.pyplot as plt


def show_mini_data():
    (x_train, t_train), = mnist.load_mnist()[:1]

    plt.imshow(x_train[0].reshape(28, 28))
    plt.show()


