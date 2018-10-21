import sys
sys.path.append('../../')

from ml_models.fire_detection import FireDetector
from ml_models.fire_detection import INPUT_HEIGHT, INPUT_WIDTH

import cv2
from glob import glob


if __name__ == '__main__':
    model = FireDetector()
    model.load_weights('../../../fire-detection-cnn/models/FireNet/firenet')

    images = glob('../../../fire-detection-cnn/test_images/*')

    for image_path in images:
        image_name = image_path.split('/')[-1]
        image = cv2.imread(image_path)
        pred = model.predict([image])[0]

        print('Image {} has fire with {:.7f}% of confidence'.format(image_name, pred * 100))
