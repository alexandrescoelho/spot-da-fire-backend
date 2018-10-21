import os

from tensorflow import float32

from tflearn import DNN
from tflearn import input_data

from tflearn.layers.core import fully_connected
from tflearn.layers.core import dropout

from tflearn.layers.conv import conv_2d
from tflearn.layers.conv import max_pool_2d

from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression

from .utils import create_logger
from .utils import reshape_image


INPUT_HEIGHT = 224
INPUT_WIDTH = 224
NUMBER_CHANNELS = 3


class FireDetector:

    def __init__(self, height=INPUT_HEIGHT, width=INPUT_WIDTH,
                 n_channels=NUMBER_CHANNELS):
        self.height = height
        self.width = width
        self.n_channels = n_channels

        self.logger = create_logger('Fire Detector')

        self._build_network()


    def _build_network(self):
        self.logger.info('Started CNN structure construction')
        network = input_data(shape=[None, self.height, self.width, 3],
                             dtype=float32)

        network = conv_2d(network, 64, 5, strides=4, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = conv_2d(network, 128, 4, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = conv_2d(network, 256, 1, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = fully_connected(network, 4096, activation='tanh')
        network = dropout(network, 0.5)

        network = fully_connected(network, 4096, activation='tanh')
        network = dropout(network, 0.5)

        network = fully_connected(network, 2, activation='softmax')

        network = regression(network, optimizer='momentum',
                             loss='categorical_crossentropy',
                             learning_rate=0.001)
        self.cnn_ = DNN(network, checkpoint_path='firenet', max_checkpoints=1,
                        tensorboard_verbose=2)
        self.logger.info('Finished CNN structure construction')


    def load_weights(self, weights_path):
        self.logger.info('Loading weights...')
        self.cnn_.load(weights_path, weights_only=True)
        self.logger.info('Weights loaded successfully')


    def predict(self, images):
        images = self._ensure_expected_shape(images)
        predictions = self.cnn_.predict(images)
        predictions = [pred[0] for pred in predictions]
        return predictions


    def _ensure_expected_shape(self, images):
        images_reshaped = []
        expected_shape = (self.height, self.width, self.n_channels)

        for img in images:
            if img.shape != (expected_shape):
                img = reshape_image(img, self.height, self.width)
            images_reshaped.append(img)

        return images_reshaped
