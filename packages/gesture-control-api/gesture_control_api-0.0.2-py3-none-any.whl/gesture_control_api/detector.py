from typing import Protocol

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model as tf_keras_load_model

from .landmarking import Landmarks

class Detector(Protocol):
    def detect_from_landmarks(self, landmarks: Landmarks) -> int:
        pass

class TfLiteDetector:
    def __init__(self, path_to_model: str):
        self.interpreter = tf.lite.Interpreter(model_path=path_to_model)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def detect_from_landmarks(self, landmarks: Landmarks) -> int:
        input_data = np.reshape(landmarks.get_underlying_storage(),
                                self.input_details[0]['shape']).astype(np.float32) # This part is still dependent on the model, get this info from input_details
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(
            self.output_details[0]['index'])
        return np.argmax(output_data[0])
    
class KerasDetector(Protocol):
    def detect_from_landmarks(self, landmarks: Landmarks) -> int:
        pass

class PyTorchDetector(Protocol):
    def detect_from_landmarks(self, landmarks: Landmarks) -> int:
        pass

class TensorflowJsDetector(Protocol):
    def detect_from_landmarks(self, landmarks: Landmarks) -> int:
        pass





# class KerasGestureDetector:
#     def __init__(self, path_to_model: str):
#         self.model = tf_keras_load_model(path_to_model, compile=False)
#         self.model.compile()
#         self.memory = [GestureCategory.NEUTRAL.value]*4
#         self.counter = 0

#         # Speed modes (every x frames gesture detection model is triggered)
#         self.slow_speed = 4
#         self.fast_speed = 1
#         self.speed_mode = self.slow_speed

#     def _model_predict(self, landmarks: Landmarks) -> int:
#         return np.argmax(self.model.predict(np.array([landmarks.get_underlying_storage()]), verbose=0))

#     def detect_gesture_from_landmarks(self, landmarks: Landmarks) -> GestureCategory:
#         if len(set(self.memory)) > 1:
#             self.speed_mode = self.fast_speed
#             # This is set to 0 so that prediction occures immediately
#             self.counter = 0
#         else:
#             self.speed_mode = self.slow_speed

#         self.counter += 1
#         if self.counter % self.speed_mode == 0:
#             cat_idx = self._model_predict(landmarks)

#             # Heuristics for better detection:
#             #
#             # Pinch: (if thumb and index finger is extremely close)
#             thumb_tip = np.array(landmarks.getPoint(lm.THUMB_TIP))
#             index_finger_tip = np.array(
#                 landmarks.getPoint(lm.INDEX_FINGER_TIP))
#             distance = np.linalg.norm(thumb_tip-index_finger_tip)
#             if cat_idx is GestureCategory.PINCH.value and distance > 0.1:
#                 cat_idx = GestureCategory.NEUTRAL.value

#             self.memory.append(cat_idx)
#             self.memory.pop(0)

#         counter = collections.Counter(self.memory)
#         return GestureCategory(counter.most_common(1)[0][0])