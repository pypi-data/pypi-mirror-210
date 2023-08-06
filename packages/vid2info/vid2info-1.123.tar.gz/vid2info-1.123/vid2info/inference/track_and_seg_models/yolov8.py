"""
This class implements the YoloDetector

Email: eric@bronze.vision
Date: 26-05-2023
"""
from __future__ import annotations
import numpy as np
import torch
from ultralytics import YOLO

import os

from vid2info.utils.parsers import yolov8_results_to_info_dict

from vid2info.inference.configs.constants import RETINA_MASKS, AUGMENT
from vid2info.inference.track_and_seg_models.track_seg_model import TrackSegModel


class YoloV8(TrackSegModel):
    def __init__(self, config_file: str):
        super().__init__(config_file=config_file)
        self.augment = self.config[AUGMENT]
        self.use_retina_masks = self.config[RETINA_MASKS]

        self.model = YOLO(model=self.model_path, task='segment')

    def predict(self, image: np.ndarray, is_bgr: bool = False) -> \
            dict[int, dict[str, int | float | dict[str, int | float | np.ndarray] | tuple[int, int] | None]]:

        assert self.model is not None, 'Model must be set before inference.'

        image = self.preprocess(image=image, is_bgr=is_bgr)

        # Predict
        results = self.model.track(source=image, tracker=self.tracker_config_file,
                                   conf=self.conf_th, iou=self.nms_iou, half=self.half_mode,
                                   device=self.device, max_det=self.max_dets, augment=self.augment,
                                   agnostic_nms=self.agnostic_nms, retina_masks=self.use_retina_masks,
                                   classes=self.filter_classes, persist=True)
        results = yolov8_results_to_info_dict(detections=results[0])

        return results
