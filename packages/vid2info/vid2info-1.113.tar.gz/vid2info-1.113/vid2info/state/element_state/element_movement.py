"""
This class implements a calculator that computes all the information related to the movement of a tracked element.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 27-02-2022
"""

from __future__ import annotations

from collections import deque
import itertools
import numpy as np

from vid2info.state.element_state.utils import frames_to_past_from_seconds_in_element_buffer
from vid2info.state.element_state.constants import STD_OUTLIER_DEVIATION, MIN_POINTS_TO_CALCULATE_OUTLIERS, \
    TOP, RIGHT, BOTTOM, LEFT


class ElementMovement:
    def __init__(self, element_state: 'ElementState', element_buffer: deque,
                 std_outlier_deviation: float = STD_OUTLIER_DEVIATION):
        """
        Initialize the ElementMovement calculator.

        :param element_state: ElementState. The element state.
        :param element_buffer: deque. The buffer containing the N previous ElementStates. It can help to compute the
                element evolution.
        """
        #TODO: Movement should be calculated in pixel space, not in percentage of the image. As it is messing the aspect ratio
        self.movement_vector_xy_1_sec = self.get_movement_vector(element_state=element_state, element_buffer=element_buffer, window_size_seconds=1)
        self.movement_1_sec_changed_significantly_xy = self.is_movement_vector_significant(element_buffer=element_buffer, movement_vector_variable='movement_vector_xy_1_sec',
                                                                                           deviation_from_std_to_be_relevant=std_outlier_deviation)
        self.movement_1_sec_changed_significantly = any(self.movement_1_sec_changed_significantly_xy)
        self.movement_1_sec_direction = self.get_movement_direction(movement_vector=self.movement_vector_xy_1_sec)
        # TODO: Could be interesting to use the area increment or decrement to infer the movement vector in Z axis.

    def get_movement_vector(self, element_state: 'ElementState', element_buffer: deque, window_size_seconds: int = 1) -> tuple[float, float]:
        """
        Compute the movement vector of the element.

        :param element_state: ElementState. The current state of the element.
        :param element_buffer: deque. The buffer containing the N previous ElementStates. It will help to compute the
                element evolution.
        :param window_size_seconds: int. The size of the window of frames to compute the movement vector.

        :return: tuple[float, float]. The movement vector of the element.
        """
        # Find the window size in frames
        curr_element_time = element_state.timestamp
        if len(element_buffer) == 0:
            return (0., 0.)

        windows_size_frames = frames_to_past_from_seconds_in_element_buffer(element_buffer=element_buffer,
                                                                            current_element_timestamp=curr_element_time,
                                                                            seconds_to_check_into_the_past=window_size_seconds)
        # Calculate the new immediate movement vector
        (curr_x, curr_y), (prev_x, prev_y) = element_state.cxcyn, element_buffer[-windows_size_frames].cxcyn
        return (prev_x - curr_x, prev_y - curr_y)

    def is_movement_vector_significant(self, element_buffer: deque, movement_vector_variable: str,
                                       seconds_to_check_into_the_past: int|None = None,
                                       deviation_from_std_to_be_relevant: float = STD_OUTLIER_DEVIATION,
                                       min_window_size_to_calculate: int = MIN_POINTS_TO_CALCULATE_OUTLIERS) -> tuple[bool, bool]:
        """
        Check if the movement vector of the element is significant.

        :param element_buffer: deque. The buffer containing the N previous ElementStates. It will help to compute the
                element evolution.
        :param movement_vector_variable: str. The name of the movement vector variable to check.
        :param seconds_to_check_into_the_past: int|None. The number of seconds to check into the past. If None, it will
                check the whole buffer.

        :return: tuple[bool, bool]. A tuple of booleans indicating if the movement vector is significant by axis.
        """
        if len(element_buffer) < min_window_size_to_calculate:
            return False, False
        windows_size_frames = frames_to_past_from_seconds_in_element_buffer(element_buffer=element_buffer,
                                                                            current_element_timestamp=element_buffer[-1].timestamp,
                                                                            seconds_to_check_into_the_past=seconds_to_check_into_the_past)
        # It is negative (from the future to the past) so we need to invert it
        window_size_beginning = len(element_buffer) - windows_size_frames

        assert hasattr(self, movement_vector_variable), f'Variable {movement_vector_variable} not found in ElementMovement'
        movement_vector = getattr(self, movement_vector_variable)
        assert len(movement_vector) == 2, f'Variable {movement_vector_variable} must be a tuple of length 2 (x, y)'
        # Get all the movement vectors of the last window_size_frames
        prev_movement_vectors = [getattr(prev_element.movement, movement_vector_variable)
                                    for prev_element in itertools.islice(element_buffer, window_size_beginning, None)]
        # Compute the standard deviation of the movement vectors
        mean, std = np.mean(prev_movement_vectors, axis=0), np.std(prev_movement_vectors, axis=0)
        # Check if the movement vector is significant (by axis)
        relevance_x, relevance_y = np.abs(mean - movement_vector) > deviation_from_std_to_be_relevant * std
        return bool(relevance_x), bool(relevance_y)

    def get_movement_direction(self, movement_vector: tuple[float, float]) -> str|None:
        """
        Get the direction of the movement vector among top, right, bottom & left (or None if (0., 0.)).

        :param movement_vector: tuple[float, float]. The movement vector.

        :return: str|None. The direction of the movement vector (or None if (0., 0.)).
        """
        assert len(movement_vector) == 2, f'Movement vector must be a tuple of length 2 (x, y)'
        x, y = movement_vector
        # Check if x or y are close to 0
        if abs(x) < 1e-5 and abs(y) < 1e-5:
            return None
        elif abs(x) > abs(y):
            return RIGHT if x > 0 else LEFT
        else:
            return BOTTOM if y > 0 else TOP

