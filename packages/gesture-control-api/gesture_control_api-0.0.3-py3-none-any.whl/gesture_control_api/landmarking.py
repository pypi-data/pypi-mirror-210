from enum import Enum
from abc import ABC, abstractmethod
from typing import List

import cv2
import mediapipe as mp

from .imaging import FrameReader

# TODO refactor this to be inside Landmarks
class LandmarkType(Enum):
    WRIST = 0
    THUMB_CNC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


class Landmarks:
    class Handedness(Enum):
        NONE = 0
        LEFT = 1
        RIGHT = 2

    def __init__(self, mediapipe_landmarks: list, handedness: Handedness = Handedness.NONE):
        self._handedness = handedness

        self.memory = []
        # Data is stored as a flat array
        # This recquires extra processing at the start, but this processing needs to be done before using the pretrained keras model, so it does not matter, except
        # It makes indexing faster
        if len(mediapipe_landmarks) > 0:
            for i in [i for i in range(21)]:
                lm = mediapipe_landmarks[i]
                self.memory.extend([lm.x, lm.y, lm.z])

    @property
    def handedness(self):
        return self._handedness
    
    def is_empty(self) -> bool:
        return len(self.memory) == 0

    def get_point(self, landmark: LandmarkType) -> tuple:
        i = landmark.value*3
        return (self.memory[i], self.memory[i+1], self.memory[i+2])

    def get_underlying_storage(self) -> list:
        return self.memory

    # Often the result of the prediction is empty, so with this segment we achieve singleton like behaviour so that empty result is only constructed once
    _empty = None

    @classmethod
    def get_empty_instance(cls):
        if cls._empty is None:
            cls._empty = cls([])
        return cls._empty


class LandmarkDetectorOneHand:
    def __init__(self, frame_reader: FrameReader, display_results=False):
        self.frame_reader = frame_reader
        self.display_results = display_results

        self.hands = mp.solutions.hands.Hands(
            model_complexity=1,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def _retrieve_coordinates(self, landmark):
        return [landmark.x, landmark.y, landmark.z]

    def detect(self) -> Landmarks:
        success, image = self.frame_reader.get_frame()

        if not success:
            # The opencv module should print a warning to stdout
            return Landmarks.get_empty_instance()

        results = self.hands.process(image)

        result = Landmarks.get_empty_instance()
        # Draw landmarks
        # This is the old api, and instead of an empty list it returns None if nothing is detected (Not a good api design:(
        if results.multi_hand_landmarks is not None:
            # Only one hand gestures are supported now
            hand_landmarks = results.multi_hand_landmarks[0]
            if self.display_results:
                mp.solutions.drawing_utils.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style())

            handedness_label = results.multi_handedness[0].classification[0].label
            handedness = Landmarks.Handedness.LEFT
            # The labels are switched up in the api (it was still prealpha when creating this)
            if handedness_label == "Left":
                handedness = Landmarks.Handedness.RIGHT

            result = Landmarks(hand_landmarks.landmark, handedness)

        if self.display_results:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow('Landmark results', image)

        return result

    def __del__(self):
        self.hands.close()
        cv2.destroyAllWindows()

# TODO inheritance hierarchi between OneHandversion
class LandmarkDetectorTwoHands:
    def __init__(self, frame_reader: FrameReader, display_results=False):
        self.frame_reader = frame_reader
        self.display_results = display_results

        self.hands = mp.solutions.hands.Hands(
            model_complexity=1,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def _retrieve_coordinates(self, landmark):
        return [landmark.x, landmark.y, landmark.z]

    # TODO hint size 2
    def detect(self) -> List[Landmarks]:
        success, image = self.frame_reader.get_frame()

        if not success:
            # The opencv module should print a warning to stdout
            return Landmarks.get_empty_instance()

        results = self.hands.process(image)

        # [Left, Right]
        result = [Landmarks.get_empty_instance(), Landmarks.get_empty_instance()]
        # Draw landmarks
        # This is the old api, and instead of an empty list it returns None if nothing is detected (Not a good api design:(
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_landmarks = results.multi_hand_landmarks[0]
                if self.display_results:
                    mp.solutions.drawing_utils.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp.solutions.hands.HAND_CONNECTIONS,
                        mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                        mp.solutions.drawing_styles.get_default_hand_connections_style())

                handedness_label = hand_handedness.classification[0].label
                # The labels are switched up in the api (it was still prealpha when creating this)
                if handedness_label == "Left":
                    result[1] = Landmarks(hand_landmarks.landmark, Landmarks.Handedness.RIGHT)
                else:
                    result[0] = Landmarks(hand_landmarks.landmark, Landmarks.Handedness.LEFT)

        if self.display_results:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow('Landmark results', image)

        return result

    def __del__(self):
        self.hands.close()
        cv2.destroyAllWindows()
