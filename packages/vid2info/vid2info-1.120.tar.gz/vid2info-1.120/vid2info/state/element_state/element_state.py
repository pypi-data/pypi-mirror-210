"""
This class implements the state of a single element on a concrete time step.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""
from __future__ import annotations
from collections import deque

from vid2info.state.element_state.constants import STD_OUTLIER_DEVIATION

from vid2info.state.element_state.element_movement import ElementMovement
from vid2info.state.finite_state_machine.element_finite_state_machine import ElementFiniteStateMachine
from vid2info.inference.config import CONFIDENCE, CLASS_ID, CLASS_NAME, BBOX_XYXY, BBOX_INFO, TRACK_INFO, TRACK_ID, \
    BBOX_WHN, BBOX_CXCYN

from time import time
import numpy as np

MANDATORY_ELEMENT_KEYS = (CONFIDENCE, CLASS_ID, BBOX_INFO)

class ElementState:
    def __init__(self, element_tracker_info : dict, first_detection_timestamp : float | None = None,
                 element_buffer : deque | None = None,
                 element_img : np.ndarray | None = None, element_segmentation_mask : dict | None = None,
                 finite_state_machine: ElementFiniteStateMachine | None = None, original_image_hw : tuple | list | None = None,
                 element_outlier_deviation_from_std: float = STD_OUTLIER_DEVIATION, is_occluded: bool = False):
        """
        Initialize the State of an element.

        :param element_tracker_info: dictionary. The information of the element, outputed from the tracker.
        :param first_detection_timestamp: float or None. If given, it is the timestamp of the first detection of this
                element.
        :param element_buffer: deque. The buffer containing the N previous ElementStates. It can help to compute the
                element evolution.
        :param element_img: np.ndarray or None. If given, it is the cropped image of the element.
        :param element_segmentation_mask: dict or None. If given, it is the dictionary containing the cropped
                                          segmentation mask of the element and the segmenter meta-information.
                                          It contains the following keys: ('segmentation_mask', 'background_class_idx',
                                            'class_names_list').
        :param finite_state_machine: ElementFiniteStateMachine or None. If given, it is the finite state machine
                                    of the element last detection, and it will be updated.

        :param element_outlier_deviation_from_std: float. The number of standard deviations from the mean that an element
                                                    movement must be to be considered an outlier.
        """
        assert all(key in element_tracker_info for key in MANDATORY_ELEMENT_KEYS), f"element_tracker_info must contain the following " \
                                                                           f"keys: {MANDATORY_ELEMENT_KEYS}. " \
                                                                           f"Got: {tuple(element_tracker_info.keys())}"

        assert type(first_detection_timestamp) is float, f"first_detection_timestamp must be a float. " \
                                                         f"It is {type(first_detection_timestamp)}"

        current_time = time()
        assert current_time >= first_detection_timestamp, f"current time must be greater than or equal to first_detection_timestamp." \
                                                          f" But current_time is  {current_time} and first_detection_timestamp is " \
                                                          f"{first_detection_timestamp}"

        self.element_info = element_tracker_info
        self.confidence = element_tracker_info[CONFIDENCE]
        self.class_id = element_tracker_info[CLASS_ID]
        self.track_id = element_tracker_info[TRACK_INFO][TRACK_ID]
        self.whn = tuple(map(float, element_tracker_info[BBOX_INFO][BBOX_WHN]))
        self.cxcyn = tuple(map(float, element_tracker_info[BBOX_INFO][BBOX_CXCYN]))

        self.first_detection_timestamp = first_detection_timestamp
        self.timestamp = current_time
        self.age_in_seconds = current_time - self.first_detection_timestamp
        self.element_buffer = element_buffer
        self.element_img = element_img
        self.movement = ElementMovement(element_state=self, element_buffer=element_buffer,
                                        std_outlier_deviation=element_outlier_deviation_from_std)

        if finite_state_machine is not None and len(self.element_buffer) > 0:
            finite_state_machine.update_state(prev_element_state=self.element_buffer[-1],
                                                   current_element_state=self)
        self.finite_state_machine = finite_state_machine



