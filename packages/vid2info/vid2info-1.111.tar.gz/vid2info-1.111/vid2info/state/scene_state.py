"""
This class implements the state of a concrete frame.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""
from __future__ import annotations
from time import time
import numpy as np

from vid2info.inference.utils import crop_bbox_from_image
from vid2info.inference.config import BBOX_XYXY, CLASS_NAME, CLASS_ID
from vid2info.state.element_state.element_state import ElementState

crop_img_if_given = lambda img, bbox, copy = True: crop_bbox_from_image(image=img, bbox_xyxy=bbox, is_normalized=True, copy=copy) \
                                        if img is not None else None

class SceneState:
    def __init__(self, track_info : dict, buffer, get_first_element_time_stamp: callable = lambda track_id : None,
                 frame: np.ndarray | None = None, segmentation_mask : dict | None = None,
                 save_full_segmentation_mask : bool = False, element_state_class : callable = ElementState,
                 element_state_machine_configs : dict | None = None):
        """
        Initialize the SceneState. It is used for defining the current scene, and will contain the
        state of each individual element in the scene.

        :param track_info: dictionary. The output of the tracker. It is the dictionary outputted by
                get_track_ids when return_as_dict is True. It's keys are the track_ids and the values are
                dictionaries with, at least, the following keys: ('bbox_xyxy', 'confidence', 'class_id', 'track_length')
        :param buffer: StateBuffer. The StateBuffer containing the N previous SceneStates.
        :param get_first_element_time_stamp: callable. A function that returns the first_timestamp of the first
                detection of the element with the given track_id in the buffer or the current timestamp if the
                element is not in the buffer.
        :param frame: np.ndarray or None. The frame of the scene. If given, it will save a cropped subimage for
                each detected element.
        :param segmentation_mask: dict or None. The segmentation mask of the scene, embedded within a dictionary
                with the following keys: ('segmentation_mask', 'background_class_idx', 'class_names_list'). If given,
                it will save a cropped subimage for each detected element.

        :param save_full_segmentation_mask: bool. If True, it will save the full segmentation mask of the scene.
        """

        self.elements = {}
        for track_id, element in track_info.items():
            element_class_name = element[CLASS_NAME] if CLASS_NAME in element else element[CLASS_ID]
            finite_state_machine = None
            if element_state_machine_configs is not None:
                finite_state_machine = buffer.get_element_state_machine(track_id=track_id, current_class=element_class_name,
                                                                        bbox_xyxy=element[BBOX_XYXY], in_scene_tracks=tuple(track_info.keys()))

            self.elements[track_id] = element_state_class(element_tracker_info=element,
                                             first_detection_timestamp=buffer.get_first_element_timestamp(track_id=track_id),
                                             element_buffer=buffer.get_element_buffer(track_id=track_id),
                                             finite_state_machine=finite_state_machine, is_occluded=self.is_element_occluded(track_id=track_id, all_elements=track_info))

        self.timestamp = time()

    def __len__(self):
        return len(self.elements)

    @property
    def older_element_timestamp(self):
        return min(element.timestamp for element in self.elements.values())

    def get_elements_age_in_seconds(self) -> dict:
        """
        Returns the age of each element in the scene in seconds.

        :return dict. The age of each element in the scene. The keys are the track_ids and
                        the values are the age in seconds.
        """
        return {track_id : self.elements[track_id].age_in_seconds for track_id in self.elements}

    def get_element_counts(self) -> dict:
        """
        Returns the number of elements in the scene for each class.

            Returns:
                dict. The number of elements in the scene for each class. The keys are the class names and
                the values are the number of elements in the scene for that class.
            """
        classes_list = [element.class_name for element in self.elements.values()]
        return {class_name: classes_list.count(class_name) for class_name in set(classes_list)}

    def elements_per_state(self) -> dict[str, set[int]]:
        """
        Returns the elements of the scene in each state.

        :return dict[str, set[int]]. The elements of the scene in each state. The keys are the state names and
                the values are the set of track_ids of the elements in that state.
        """
        states = {}
        for _id, element in self.elements.items():
            state_machine = element.finite_state_machine
            if state_machine is not None:
                state = state_machine.current_state
                if state not in states:
                    states[state] = set()
                states[state].add(_id)
        return states

    def is_element_occluded(self, track_id, all_elements):
        # TODO: Implement it.
        return False
