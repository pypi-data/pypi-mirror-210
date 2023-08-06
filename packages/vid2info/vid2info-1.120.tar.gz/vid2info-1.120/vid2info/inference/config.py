import os
import torch

GENERAL_MODELS_PATH = os.path.join('.', 'vid2info', 'inference', 'models')

BBOX_INFO, SEGMENTATION_INFO, TRACK_INFO = 'bbox_info', 'segmentation_info', 'track_info'

XMIN, YMIN, XMAX, YMAX = 'xmin', 'ymin', 'xmax', 'ymax'
XNMIN, YNMIN, XNMAX, YNMAX = 'xnmin', 'ynmin', 'xnmax', 'ynmax'
BBOX_WH, BBOX_WHN, BBOX_XYXY, BBOX_XYXYN = 'bbox_wh', 'bbox_whn', 'bbox_xyxy', 'bbox_xyxyn'
BBOX_CXCY, BBOX_CXCYN = 'bbox_cxcy', 'bbox_cxcyn'
CONFIDENCE, CLASS_ID, CLASS_NAME = 'confidence', 'class_id', 'class_name'

POLYGON_XY, POLYGON_XYN = 'polygon_xy', 'polygon_xyn'

TRACK_ID = 'track_id'

IMAGE_HW = 'image_hw'
TIMESTAMP = 'timestamp'

BACKGROUND_CLASS_IDX = 'background_class_idx'

UINT8_TO_FLOAT = 1/255

DEFAULT_DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')