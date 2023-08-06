"""
This class implements the Pipeline of the inference. It will use a raw frame of the video as input,
and will output a State object, with the current situation.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 16-07-2022
"""
from __future__ import annotations

import os

from utils.parsers import yolov8_results_to_info_dict
from vid2info.inference.segmentation.yolov8 import YoloV8
from vid2info.state.finite_state_machine.track_recoverer import TrackRecoverer

from vid2info.state.state_buffer import StateBuffer
from vid2info.state.scene_state import SceneState
from vid2info.state.element_state.element_state import ElementState


from vid2info.video.config import DEFAULT_VIDEO_FRAME_RATE

from ultralytics import YOLO
from loguru import logger
import numpy as np
from collections import deque
from time import time
import cv2

FRAME_RATE_BUFFER_SIZE = 8 # Frames

TRACKER_CONF_FILE_PATH = os.path.join('vid2info','inference', 'models', 'bytetrack.yaml')
MODEL_PT_PATH = os.path.join('vid2info','inference', 'models', 'segmentation', 'yolov8n-seg.pt')

class Pipeline:
    def __init__(self, detector_model_path: str = MODEL_PT_PATH, video_frame_rate: int | None = DEFAULT_VIDEO_FRAME_RATE,
                 element_state_class: type = ElementState, scene_state_class : type = SceneState,
                 finite_state_machine_config: dict | None = None,
                 save_images_in_scene_state: bool = True,
                 tracker_recoverer: TrackRecoverer | None = None,
                 inference_device : str = None):
        """
        Initialize the Pipeline. It will use a raw frame of the video as input, and will output a State object,
        with the current situation.

        :param detector_model_path: string. Path to the weights of the detector.
        :param video_frame_rate: int. Frame rate of the video that outputs each frame. It is relevant
                for the tracker. If video is coming from a webcam working on the fly, it should be None.
                In this case the pipeline will track the empirical frame rate at which we are calling it,
                and will keepit synchronized.
        :param original_img_hw: tuple. The original size of the image that is going to be processed. It is,
                the size of the original_video that we are processing.

        :param detector_dataset_yml: string. Path to the dataset yml file of the detector. It will be used to
                load the labels of the classes.
        :param max_detections_per_img: int. Maximum number of detections per image.
        :param detector_confidence_th: float. Minimum confidence threshold for the detector.
        :param nms_th: float. IOU threshold for the non-max suppression of the detector.
        :param agnostic_nms: bool. If True, the detector will not use the class id when performing the nms.
        :param use_only_high_confidence_detection: bool. If True, only high confidence detections will be used as
        input to the tracker. Otherwise, all the tracker will receive all the detections above the detector
        confidence threshold, together with all the detections below the tracker confidence threshold.

        :param track_th: Float. The threshold to consider a track as valid.
        :param match_thresh: Float. The threshold to consider a match between two tracks.
        :param track_buffer: Int. The number of frames to keep the track in the buffer.

        :param segmenter_model_path: string or None. Path to the weights of the segmenter. If None,
                the segmenter will not be used.
        :param segmenter_params_path: string. Path to the yml file with the segmenter params. If segmenter_model_path
                is None, this parameter will be ignored.
        :param segmenter_model_name: string. Name of the segmenter model (must end with 'small', 'medium' or 'large').
                If segmenter_model_path is None, this parameter will be ignored.

        :param element_state_class: type. The class to use for the element state. It should inherit from
                                vid2info.state.element_state.ElementState. This class will be used for implementing all
                                the Bronze Specific State management logic.
        :param scene_state_class: type. The class to use for the scene state. It should inherit from
                                vid2info.state.scene_state.SceneState. This class will be used for implementing all
                                the Bronze Specific State management logic (with the information of all the Elements
                                in the scene).
        :param save_images_in_scene_state: bool. If True, a cropped image of the detected element will be saved
                                                in the scene state.
        :param finite_state_machine_config: dict. Configuration of the finite state machine.
        :param merge_batch_detections: Boolean. Whether to merge batches or not. If it is True, and the input is a batch
                                of images, predictions will be merged as if they came from a single image. It is only
                                recommended for very static scenes.

        :param recover_tracks_for_static_elements: bool. Only used when finite_state_machines_config is passed.
                If True, it will try to recover the tracks for the elements with a class that fallbacks in a default
                state machine. NOTE: It should ONLY be used when we are expecting very STATIC elements that do not tend
                to overlap with each other. Otherwise, it could produce unexpected results. The expected scenario for
                this flag is when we do expect static elements, that can be partially lost by occlusions, and that have
                an attached state machine that makes transitions based in the object class but that only accept a few
                 entry classes but the classes. For example: A lot of robotic faces that always starts with the class
                 "neutral expression" and for which we are registering the expression transitions.

        :param inference_device: string. Device to use for the inference. It can be 'cpu' or 'cuda'.
        :param half_mode: bool. If True, the models will be loaded in half precision. Only valid when inference_device
                is 'cuda'.
        """

        self.model = YOLO(model=detector_model_path, task='segment') #YoloV8(pt_path=detector_model_path, inference_device='cpu', half_mode=False)


        # Set all the structures for keeping the frame_rate updated in case it is being read online
        self.running_online = video_frame_rate is None
        self.video_frame_rate_track = deque(maxlen=FRAME_RATE_BUFFER_SIZE) if self.running_online else None

        self.save_images_in_scene_state = save_images_in_scene_state
        self.state_buffer = StateBuffer(buffer_size=100, running_online=self.running_online,
                                        element_state_class=element_state_class, scene_state_class=scene_state_class,
                                        finite_state_machines_config=finite_state_machine_config,
                                        track_recoverer=tracker_recoverer,
                                        keep_elements_history=finite_state_machine_config is not None)

    @property
    def fps(self) -> float | None:
        """
        Return the current frame rate of the video.

        :return: float. The current frame rate of the video.
        """
        if self.video_frame_rate_track is not None and len(self.video_frame_rate_track) > 1:
            return 1 / (np.mean(np.diff(self.video_frame_rate_track)))
        else:
            logger.debug("Frame rate information is not available yet. Returning None")
            return None

    def process_frame(self, frame: np.ndarray, is_bgr : bool = False) -> SceneState:
        """
        Process a frame and return its SceneState.

        NOTE: Take into account that it will automatically state buffer. So, to keep it consistent,
            you should always call this function with consecutive frames.

        :param frame: np.ndarray. Raw frame to process. In the format (H, W, C). With three channels
                (BGR or RGB).
        :param is_bgr: bool. If True, the frame is in BGR format. If False, it is in RGB format.

        :return: The SceneState of the given frame. It will contain each one of the element detections
                 together with its track.
        """
        assert frame.ndim == 3 and frame.shape[2] == 3, f"Frame must be in the format (H, W, C) with C=3. " \
                                                        f"Got {frame.shape}"
        if is_bgr:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Update the frame rate if it is being read online
        if self.running_online:
            # Keep track of the timestasmps at which each frame is processed
            self.video_frame_rate_track.append(time())

        # Detect the objects in the frame
        detections = self.model.track(frame, tracker=TRACKER_CONF_FILE_PATH, iou=0.5, classes=0, persist=True)
        track_info = yolov8_results_to_info_dict(detections=detections[0])
        # Update the state buffer
        scene_state = self.state_buffer.build_scene_state(track_info=track_info, add_to_buffer=True,
                                                          frame=frame if self.save_images_in_scene_state else None)

        return scene_state
