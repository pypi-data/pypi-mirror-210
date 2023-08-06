from __future__ import annotations

import numpy as np
from ultralytics.yolo.engine.results import Results
from time import time

from inference.config import POLYGON_XY, POLYGON_XYN, CLASS_ID, CLASS_NAME, CONFIDENCE, TRACK_INFO, TRACK_ID, BBOX_INFO, \
    XNMIN, YNMIN, XNMAX, YNMAX, XMIN, YMIN, XMAX, YMAX, BBOX_XYXY, BBOX_XYXYN, SEGMENTATION_INFO, IMAGE_HW, TIMESTAMP, \
    BBOX_WH, BBOX_WHN, BBOX_CXCY, BBOX_CXCYN


def yolov8_results_to_info_dict(detections: Results) -> dict[int, dict[str, int | float | dict[str, int | float | np.ndarray] | tuple[int, int] | None]]:
    """
    Convert the detections format of YOLOv8 to a dictionary. This cast is useful to separate our logical structure
    from the YOLOv8 implementation. This way, we could easily change the model without affecting the rest of the code.

    :param detections: The detections returned by the YOLOv8 model.
    :return: A dictionary where the keys are track ids and the values are
                another dictionary with detailed detection info.
    """
    tracks = {}

    for detection in detections:
        boxes = detection.boxes.numpy()

        # Validate the box format
        assert len(boxes.xyxyn) == 1, f'Expected only one xyxyn bbox per detection. Got {len(boxes.xyxyn)}.'
        assert len(boxes.xyxy) == 1, f'Expected only one xyxy bbox per detection. Got {len(boxes.xyxy)}.'
        xn_min, yn_min, xn_max, yn_max = map(float, boxes.xyxyn[0])
        x_min, y_min, x_max, y_max = map(float, boxes.xyxy[0])

        track_id, class_id = int(boxes.id), int(boxes.cls)
        confidence = float(boxes.conf)

        # Initialize segmentation_info to None, update it if masks are present
        segmentation_info = None
        if 'masks' in detection.keys:
            # Validate the mask format
            assert len(detection.masks.xy) == 1, f'Expected only one xy polygon per detection. Got {len(detection.masks.xy)}.'
            assert len(detection.masks.xyn) == 1, f'Expected only one xyn polygon per detection. Got {len(detection.masks.xyn)}.'

            # Masks won't be saved, only polygons, to avoid memory issues
            segmentation_info = {POLYGON_XY: detection.masks.xy[0],
                                 POLYGON_XYN: detection.masks.xyn[0]}

        # Store all the information in the tracks dictionary
        tracks[track_id] = {
            CLASS_ID: class_id,
            CLASS_NAME: detection.names[class_id],
            CONFIDENCE: confidence,
            TRACK_INFO: {
                TRACK_ID: track_id,
            },
            BBOX_INFO: {
                XNMIN: xn_min, YNMIN: yn_min, XNMAX: xn_max, YNMAX: yn_max,
                XMIN: x_min, YMIN: y_min, XMAX: x_max, YMAX: y_max,
                BBOX_XYXY: boxes.xyxy[0],
                BBOX_XYXYN: boxes.xyxyn[0],
                BBOX_WH: boxes.xywh[0, 2:],
                BBOX_WHN: boxes.xywhn[0, 2:],
                BBOX_CXCY: boxes.xywh[0, :2],
                BBOX_CXCYN: boxes.xywhn[0, :2],
            },
            SEGMENTATION_INFO: segmentation_info,
            IMAGE_HW: detection.orig_shape,
            TIMESTAMP: time(),
        }

    return tracks
