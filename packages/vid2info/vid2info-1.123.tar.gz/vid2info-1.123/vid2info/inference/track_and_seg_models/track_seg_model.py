"""
This class is an interface for models that can track and segment objects in a video.

Email: eric@bronze.vision
Date: 26-05-2023
"""
from __future__ import annotations
import numpy as np
import torch
from ultralytics import YOLO

import os

from vid2info.inference.configs.constants import CLASSES, MAX_DETS, AGNOSTIC_NMS, TRACKER_CONFIG
from vid2info.inference.model_interface import Model


class TrackSegModel(Model):
    def __init__(self, config_file: str):
        super().__init__(config_file=config_file)
        self.max_dets = self.config[MAX_DETS]
        self.filter_classes = self.config[CLASSES]
        self.agnostic_nms = self.config[AGNOSTIC_NMS]

        self.tracker_config_file = os.path.normpath(os.path.join(os.path.dirname(config_file), self.config[TRACKER_CONFIG]))

        self.model = None