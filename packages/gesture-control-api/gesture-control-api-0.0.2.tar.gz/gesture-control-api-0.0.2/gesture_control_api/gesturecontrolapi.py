from enum import Enum

from .landmarking import LandmarkDetectorOneHand, LandmarkDetectorTwoHands
from .gesturemodel import GestureModel, ActionDetectGestureModel, RobustGestureModel
from .cameracontrol import Camera3D, CameraMode, NoAlterMode


class GestureControlAlgorithmFor3DSoftware:
    def __init__(self, landmarker: LandmarkDetectorOneHand, gesture_model: GestureModel, camera: Camera3D):
        self.landmarker = landmarker
        self.gesture_model = gesture_model
        self.camera = camera

        self.gesture_actions = {}

        self.previous_category = None
        self.default_mode = NoAlterMode()
        self.camera_mode = self.default_mode

    def do(self, category: Enum, camera_mode: CameraMode):
        key = str(category)

        if key in self.gesture_actions:
            raise ValueError(f"Parameter 'category': {category} already added as action trigger.")
        
        self.gesture_actions[key] = camera_mode

    def run_once(self) -> Camera3D:
        landmarks = self.landmarker.detect()

        if not landmarks.is_empty():
            category = self.gesture_model.predict_gesture_from_landmarks(landmarks)
                
            if (self.previous_category != category):
                try:
                    self.camera_mode = self.gesture_actions[str(category)]
                    self.camera_mode.set_state(landmarks, self.camera)
                except KeyError:
                    # If an action was not set nothing should happen with the camera by default
                    self.camera_mode = self.default_mode
               
                self.previous_category = category
                
            self.camera_mode.alter_camera(landmarks, self.camera)

        return self.camera
    

class GestureControlAlgorithmFor3DSoftwareWith2HandsDemo(GestureControlAlgorithmFor3DSoftware):
    def __init__(self, landmarker: LandmarkDetectorTwoHands, gesture_model: GestureModel, camera: Camera3D):
        super().__init__(landmarker, gesture_model, camera)

        self.two_hand_landmarker = landmarker
        self.action_category_predictor = ActionDetectGestureModel()

    def run_once(self) -> Camera3D:
        left, right = self.two_hand_landmarker.detect() # Left right prediction doesn't work

        if not left.is_empty() and not right.is_empty():
            left_category = self.gesture_model.predict_gesture_from_landmarks(left)
            right_category = self.gesture_model.predict_gesture_from_landmarks(right)

            category = None
            if left_category is RobustGestureModel.GestureCategory.FIST:
                category = right_category
            elif right_category is RobustGestureModel.GestureCategory.FIST:
                category = left_category
            else:
                return self.camera

            if (self.previous_category != category):
                try:
                    self.camera_mode = self.gesture_actions[str(category)]
                    self.camera_mode.set_state(right, self.camera)
                except KeyError:
                    # If an action was not set nothing should happen with the camera by default
                    self.camera_mode = self.default_mode
            
                self.previous_category = category
                
            self.camera_mode.alter_camera(right, self.camera)

        return self.camera
    