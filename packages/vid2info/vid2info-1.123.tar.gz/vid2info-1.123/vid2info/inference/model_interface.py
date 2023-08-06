"""
This class implements the YoloDetector

Email: eric@bronze.vision
Date: 26-05-2023
"""
from __future__ import annotations
import yaml
import numpy as np
import torch
import cv2
from ultralytics import YOLO
from loguru import logger
import os

from vid2info.inference.detection.config import HALF_MODE

from vid2info.inference.configs.constants import CONF_TH, NMS_IOU, MODEL_PATH


class Model:
    def __init__(self, config_file: str):
        # Read the yaml file
        with open(config_file, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        self.model_path = os.path.normpath(os.path.join(os.path.dirname(config_file), self.config[MODEL_PATH]))

        self.conf_th, self.nms_iou = self.config[CONF_TH], self.config[NMS_IOU]
        self.device = self.__select_device(self.config['device'])
        self.half_mode = self.config[HALF_MODE] if self.device.type != 'cpu' else False

        self.model = None # Must be set in the child class

    def __select_device(self, device: str) -> torch.device:
        """
        Selects the device to use for inference.

        :param device: String. The device to use for inference.
        :return: The device to use for inference.
        """
        if device is None:
            device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
            logger.info(f'Using {device} for inference.')
            return torch.device(device)
        if device == 'cpu':
            return torch.device('cpu')
        else:
            assert device.startswith('cuda'), f'Inference device must be cpu or cuda. Got {device}.'
            return torch.device(device)

    def preprocess(self, image: np.ndarray, is_bgr: bool = False):
        """
        Preprocesses the image for inference.

        :param image: Numpy array. The image to preprocess.
        :param is_bgr: Boolean. Whether the image is in BGR format.
        :return: The preprocessed image.
        """
        if is_bgr:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def predict(self, image: np.ndarray, is_bgr: bool = False) -> np.ndarray:
        """
        Predicts the bounding boxes and classes of the given image.

        :param image: Numpy array. The image to predict the bounding boxes and classes of.
        :return: Tuple of two numpy arrays. The first one contains the bounding boxes in the format (x, y, w, h) and the
                    second one contains the classes.
        """
        assert self.model is not None, 'Model must be set in the child class.'
        raise NotImplementedError('predict() must be implemented in the child class.')