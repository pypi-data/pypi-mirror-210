from abc import ABC, abstractmethod
from enum import Enum
import collections

import numpy as np

from .landmarking import Landmarks, LandmarkType
from .detector import TfLiteDetector


class GestureModel(ABC):
    @abstractmethod
    def predict_gesture_from_landmarks(self, landmarks: Landmarks) -> Enum:
        pass


class RobustGestureModel(GestureModel):
    class GestureCategory(Enum):
        NEUTRAL = 0
        PINCH = 1
        POINT_WITH_INDEX_AND_MIDDLE = 2
        FIST = 3
        PINCH_CLOSED_HAND = 4

    def __init__(self, path_to_model="machine_learning_models/robust_model_4.tflite"):
        self.detector = TfLiteDetector(path_to_model)

        self.memory = [self.GestureCategory.NEUTRAL.value] * 4

    def predict_gesture_from_landmarks(self, landmarks: Landmarks) -> GestureCategory:
        cat_idx = self.detector.detect_from_landmarks(landmarks)

        # Heuristics
        thumb_tip = np.array(landmarks.get_point(LandmarkType.THUMB_TIP))
        index_finger_tip = np.array(
            landmarks.get_point(LandmarkType.INDEX_FINGER_TIP))
        distance = np.linalg.norm(thumb_tip-index_finger_tip)
        if cat_idx is self.GestureCategory.PINCH.value and distance > 0.1:
            cat_idx = self.GestureCategory.NEUTRAL.value

        self.memory.append(cat_idx)
        self.memory.pop(0)

        counter = collections.Counter(self.memory)
        return self.GestureCategory(counter.most_common(1)[0][0])


class ActionDetectGestureModel(GestureModel):
    class GestureCategory(Enum):
        NOACTION = 0
        ACTION = 1

    def __init__(self):
        self.robust_model = RobustGestureModel()

    def predict_gesture_from_landmarks(self, landmarks: Landmarks) -> GestureCategory:
        robust_model_category = self.robust_model.predict_gesture_from_landmarks(landmarks)
        if robust_model_category is RobustGestureModel.GestureCategory.FIST:
            return self.GestureCategory.ACTION
        else:
            return self.GestureCategory.NOACTION
