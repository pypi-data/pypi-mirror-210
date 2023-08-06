from __future__ import annotations

from collections import deque


def frames_to_past_from_seconds_in_element_buffer(element_buffer: deque, current_element_timestamp: float,
                                                  seconds_to_check_into_the_past: int|float|None) -> int:
        """
        Compute the number of frames that have been recorded in the buffer that are older than the given number of
        seconds.

        :param element_buffer: deque. The buffer containing the N previous ElementStates. It will help to compute the
                element evolution.
        :param current_element_timestamp: float. The timestamp of the current element.
        :param seconds_to_check_into_the_past: int|float|None. The number of seconds to check into the past. If None, it will
                just return the length of the buffer.

        :return: int. The number of frames that have been recorded in the buffer that are older than the given number of
                seconds.
        """
        windows_size_frames = len(element_buffer)
        if seconds_to_check_into_the_past is not None and windows_size_frames > 1:
            assert seconds_to_check_into_the_past > 0., 'The number of seconds to check into the past must be positive.'
            for i in range(1, windows_size_frames + 1):
                # Find the first element that is older than window_size_seconds
                if current_element_timestamp - element_buffer[-i].timestamp > seconds_to_check_into_the_past:
                    windows_size_frames = i
                    break
        return windows_size_frames
