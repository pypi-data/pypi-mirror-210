"""
This class implements the Stream Visualization. It will display the current stream of video that is being
processed with all the annotations of the current scene state.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""
from __future__ import annotations
import os
from loguru import logger

import cv2
import numpy as np

from inference.config import SEGMENTATION_INFO, POLYGON_XYN
from vid2info.video.config import DEFAULT_VIDEO_FRAME_RATE

from vid2info.state.scene_state import SceneState

from vid2info.visualization.config import DEFAULT_WINDOW_SIZE_HW, KEEP_ORIGINAL_ASPECT_RATIO, DEFAULT_WINDOW_NAME, \
    TRACK_ID, CLASS, COLOR_BY_OPTIONS, BBOXES_COLOR_MAP, MAX_BBOX_COLORS
from vid2info.visualization.overlay_utils import overlay_annotations


class StreamVisualization:
    def __init__(self, window_size_hw: tuple[int, int] | list[int, int] | None = DEFAULT_WINDOW_SIZE_HW,
                 keep_original_aspect_ratio: bool = KEEP_ORIGINAL_ASPECT_RATIO,
                 window_name: str = DEFAULT_WINDOW_NAME, color_by: str = TRACK_ID,
                 save_output_at: str | None = None, save_output_fps: int = DEFAULT_VIDEO_FRAME_RATE):
        """
        Initialize the StreamVisualization. It will display the current stream of video that is being
        processed with all the annotations of the current scene state. You must use the show() method to
        display the stream and the update() method to update the visualization. You can also use "with",
        to automatically display it.

        :param window_size_hw: tuple. The size of the window in (height, width). If keep_original_aspect_ratio is True,
                only one of the two dimensions will be used, and the other one will be calculated to keep the
                original aspect ratio of the input image.
        :param keep_original_aspect_ratio: bool. If True, the window will be resized to keep the original aspect ratio
                of the input image.
        :param window_name: str. The name of the window.
        :param color_by: str. The color by which the annotations will be colored. Accepted values are:
                - 'track_id': Color by track ID.
                - 'class': Color by class.
        :param save_output_at: str. If not None, the visualization will be saved at the given path.
        """
        assert color_by in COLOR_BY_OPTIONS, f"color_by must be one of: {COLOR_BY_OPTIONS}. Got: {color_by}"
        self.window_size_hw = window_size_hw
        self.keep_original_aspect_ratio = keep_original_aspect_ratio
        self.window_name = window_name
        self.color_by = color_by
        if save_output_at is not None:
            # Change the extension to .mp4
            save_output_at = os.path.splitext(save_output_at)[0] + ".mp4"
            if os.path.exists(save_output_at):
                logger.warning(f"Overwriting existing file: {save_output_at}")
            # Create the video writer
            self.video_writer = cv2.VideoWriter(filename=save_output_at,
                                                fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
                                                frameSize=self.window_size_hw[::-1],
                                                fps=save_output_fps)
        else:
            self.video_writer = None

        # Create the cv2 window that we will be updating later
        cv2.namedWindow(winname=self.window_name, flags=cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(winname=self.window_name, x=0, y=0)
        cv2.setWindowTitle(winname=self.window_name, title=self.window_name)
        cv2.waitKey(delay=1)

    def update(self, image: np.ndarray, scene_state: SceneState, image_is_bgr = True,
               overlay_annotations_function: callable = overlay_annotations) -> np.ndarray:
        """
        Update the visualization with the given image and scene state. And shows it in the window.


        :param image: np.ndarray. The image to display.
        :param scene_state: SceneState. The scene state to display.
        :param image_is_bgr: bool. If True, the image is assumed to be in BGR format,
                otherwise it is assumed to be in RGB format.

        :return np.ndarray. The image that was displayed.

        :exception InterruptedError: If the user pressed have closed the window.
        """
        assert image.ndim == 3, f"image must be 3D. Got: {image.shape}"
        assert image.shape[2] == 3, f"image must have 3 channels. Got: {image.shape}"
        assert issubclass(type(scene_state), SceneState), f"scene_state must be of type SceneState (or inherit from it)," \
                                       f"but it is {type(scene_state)}"

        if cv2.getWindowProperty(winname=self.window_name, prop_id=cv2.WND_PROP_VISIBLE) < 1:
            # Exit if the window is not visible
            raise InterruptedError("User has closed the visualization window")

        image = self.draw_segmentation_masks(image = image, scene_state = scene_state)

        # Overlay the annotations on the image
        #image = overlay_annotations_function(image=image, scene_state=scene_state, is_bgr=image_is_bgr,
                                    #color_by=self.color_by)

        # Resize the image if necessary
        if self.window_size_hw is not None:
            image = self.resize_image(image=image, new_size_hw=self.window_size_hw)

        if not image_is_bgr:
            # Convert to BGR if necessary
            image = cv2.cvtColor(src=image, code=cv2.COLOR_RGB2BGR)

        # Show it
        cv2.imshow(winname=self.window_name, mat=image)
        cv2.waitKey(delay=1)
        # Write the frame to the video writer if necessary
        if self.video_writer is not None:
            self.video_writer.write(image)

        return image

    def draw_segmentation_masks(self, image: np.ndarray, scene_state: SceneState):
        """
        Draws all the polygons over the image.
        """
        for track_id, element in scene_state.elements.items():
            if self.color_by == TRACK_ID:
                color = BBOXES_COLOR_MAP(track_id*(BBOXES_COLOR_MAP.N//MAX_BBOX_COLORS) % (BBOXES_COLOR_MAP.N + 1))[:3]
            elif self.color_by == CLASS:
                color = BBOXES_COLOR_MAP(element.class_id*(BBOXES_COLOR_MAP.N//MAX_BBOX_COLORS) % (BBOXES_COLOR_MAP.N + 1))[:3]

            segmentation_info = element.element_info[SEGMENTATION_INFO]
            assert segmentation_info is not None, f"element_info must contain a segmentation_info key. Got: {element.element_info}"
            polygon = segmentation_info[POLYGON_XYN]
            # Transform from normalized to image coordinates
            polygon = polygon * image.shape[:2][::-1]
            polygon = polygon.astype(np.int32)

            # Draw the polygon on the image
            cv2.polylines(image, [polygon], isClosed=True, color=color, thickness=1)

        return image



    def resize_image(self, image : np.ndarray,
                     new_size_hw : tuple[int, int] | list[int, int] | np.ndarray) -> np.ndarray:
        """
        Resizes the image to self.window_size_hw, being aware of the keeping the original aspect ratio
        if self.keep_original_aspect_ratio is True.

        Args:
            image: np.ndarray. The image to resize.

        Returns:
            np.ndarray. The resized image.
        """
        assert type(new_size_hw) in (list, tuple, np.ndarray), f"new_size_hw must be a tuple or list." \
                                                               f" Got: {type(new_size_hw)}"
        assert len(new_size_hw) == 2, f"new_size_hw must be an iterable of length 2. Got: {len(new_size_hw)}"
        h, w = image.shape[:2]
        new_h, new_w = new_size_hw
        if self.keep_original_aspect_ratio:
            if h > w:
                new_w = int(new_h * w / h)
            else:
                new_h = int(new_w * h / w)
        if (h, w) != (new_h, new_w):
            image = cv2.resize(src=image, dsize=(new_w, new_h))
        return image

    def __enter__(self):
        """
        Enter the with block.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the with block.

        Args:
            exc_type: Exception. The type of the exception.
            exc_val: Exception. The value of the exception.
            exc_tb: Exception. The traceback of the exception.
        """
        self.close()

    def __del__(self):
        """
        Destructor.
        """
        self.close()

    def close(self):
        """
        Close the window.
        """
        if cv2.getWindowProperty(winname=self.window_name, prop_id=cv2.WND_PROP_VISIBLE) > 0:
            cv2.destroyWindow(winname=self.window_name)
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None