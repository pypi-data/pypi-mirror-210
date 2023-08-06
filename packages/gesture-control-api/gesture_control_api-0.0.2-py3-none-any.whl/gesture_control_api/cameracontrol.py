from abc import ABC, abstractmethod

import numpy as np

from .landmarking import Landmarks, LandmarkType as lm


def rotate_vector_around_axis(vector: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    return vector*np.cos(angle) + np.cross(axis, vector)*np.sin(angle) + axis*np.dot(axis, vector)*(1 - np.cos(angle))


class Camera3D:
    def __init__(self, location: np.ndarray, focus_point: np.ndarray):
        self._location = location
        self._focus_point = focus_point

        self._changed = False

    # TODO Might not be set properly now
    @property
    def changed(self) -> bool:
        return self._changed

    @changed.setter
    def changed(self, value: bool):
        self.changed = value

    @property
    def location(self) -> np.ndarray:
        return self._location

    @location.setter
    def location(self, value: np.ndarray):
        self._location = value

    @property
    def focus_point(self) -> np.ndarray:
        return self._focus_point

    @focus_point.setter
    def focus_point(self, value: np.ndarray):
        self._focus_point = value

    def get_gaze_direction(self) -> np.ndarray:
        return self._focus_point - self._location


class CameraMode(ABC):
    @abstractmethod
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        pass

    @abstractmethod
    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        pass


class DragLandscapeModeOld(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.tiltOrigin = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.focusPoint = camera.focus_point
        self.camRelativeToFocusPoint = camera.location() - self.focusPoint
        self.smoothingFactor = 5
        self.prevDxList = [0.0] * self.smoothingFactor
        self.prevDyList = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x_c, y_c, _) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        # proportional to horizontal rotation
        dx = 3.8 * (x_c - self.tiltOrigin[0])
        # proportional to lateral rotation
        dy = -3.8 * (y_c - self.tiltOrigin[1])

        # Kalman filter
        self.prevDxList.append(dx)
        self.prevDxList.pop(0)
        self.prevDyList.append(dy)
        self.prevDyList.pop(0)
        average_dx = sum(self.prevDxList) / self.smoothingFactor
        average_dy = sum(self.prevDyList) / self.smoothingFactor

        # Math for rotating around focuspoint
        up = np.array([0, 0, 1])
        axis = np.cross(up, self.camRelativeToFocusPoint)
        horizontally_rotated_vector = rotate_vector_around_axis(
            self.camRelativeToFocusPoint,
            axis,
            average_dy
        )
        laterally_and_horizontally_rotated_vector = rotate_vector_around_axis(
            horizontally_rotated_vector,
            up,
            average_dx
        )

        # Can't go "underground"
        if (laterally_and_horizontally_rotated_vector[2] < 0.1):
            laterally_and_horizontally_rotated_vector[2] = 0.1

        new_cam_pos = self.focusPoint + laterally_and_horizontally_rotated_vector

        camera.location = new_cam_pos
        camera.focus_point = self.focusPoint


class TiltCameraModeOld(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.tiltOrigin = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.gazeDirectionBeforeTilt = camera.get_gaze_direction()
        self.smoothingFactor = 10
        self.prevDxList = [0.0] * self.smoothingFactor
        self.prevDyList = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x, y, z) = self.tiltOrigin
        (x_c, y_c, z_c) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        dx = 2.5 * (x_c - x)  # proportional to horizontal rotation
        dy = -2.5 * (y_c - y)  # proportional to lateral rotation

        # Kalman filter
        self.prevDxList.append(dx)
        self.prevDxList.pop(0)
        self.prevDyList.append(dy)
        self.prevDyList.pop(0)
        average_dx = sum(self.prevDxList) / self.smoothingFactor
        average_dy = sum(self.prevDyList) / self.smoothingFactor

        cam_pos_vector = camera.location
        gaze_direction = camera.get_gaze_direction()

        axis = np.cross(gaze_direction, np.array([0, 0, 1]))
        gaze_direction = rotate_vector_around_axis(
            self.gazeDirectionBeforeTilt,
            axis,
            average_dy
        )
        gaze_direction = rotate_vector_around_axis(
            gaze_direction, np.array([0, 0, 1]), average_dx)

        new_focus_point = cam_pos_vector + gaze_direction

        camera.focus_point = new_focus_point


class ZoomModeOld(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.referencePoint = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.camBeforeTransform = camera.location
        self.smoothingFactor = 5
        self.prevZoomFactors = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x, y, z) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        (x_r, y_r, z_r) = self.referencePoint
        zoomFactor = -2 * (x - x_r)

        # Kalman filter
        self.prevZoomFactors.append(zoomFactor)
        self.prevZoomFactors.pop(0)
        averageZoomFactor = sum(self.prevZoomFactors) / self.smoothingFactor

        gazeDirection = camera.get_gaze_direction()
        offset = gazeDirection * averageZoomFactor
        newCamPos = self.camBeforeTransform + offset

        # Can't go "underground"
        if newCamPos[2] > 0.1:
            camera.location = newCamPos


class NoAlterMode(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        pass

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        pass


class DragLandscapeModeMultiObj(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.tiltOrigin = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.focusPoint = self._calc_focus(camera)
        self.camRelativeToFocusPoint = camera.location - self.focusPoint
        self.smoothingFactor = 5
        self.prevDxList = [0.0] * self.smoothingFactor
        self.prevDyList = [0.0] * self.smoothingFactor

    def _calc_focus(self, camera: Camera3D) -> np.ndarray:
        pos = camera.location
        gaze = camera.get_gaze_direction()
        t = (-pos[2]/gaze[2])

        # dealing with looking up
        self.invalid_focus = False
        if t < 0:
            self.invalid_focus = True

        return pos + gaze * t

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        if self.invalid_focus:
            return camera

        (x_c, y_c, _) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        # proportional to horizontal rotation
        dx = 3.8 * (x_c - self.tiltOrigin[0])
        # proportional to lateral rotation
        dy = -3.8 * (y_c - self.tiltOrigin[1])

        # Kalman filter
        self.prevDxList.append(dx)
        self.prevDxList.pop(0)
        self.prevDyList.append(dy)
        self.prevDyList.pop(0)
        average_dx = sum(self.prevDxList) / self.smoothingFactor
        average_dy = sum(self.prevDyList) / self.smoothingFactor

        # Math for rotating around focuspoint
        up = np.array([0, 0, 1])
        axis = np.cross(up, self.camRelativeToFocusPoint)
        horizontallyRotatedVector = rotate_vector_around_axis(
            self.camRelativeToFocusPoint,
            axis,
            average_dy
        )
        LaterallyAndHorizontallyRotatedVector = rotate_vector_around_axis(
            horizontallyRotatedVector,
            up,
            average_dx
        )

        # Can't go "underground", but can still move left and right
        if (LaterallyAndHorizontallyRotatedVector[2] < 0.1):
            LaterallyAndHorizontallyRotatedVector[2] = 0.1

        camera.location = self.focusPoint + LaterallyAndHorizontallyRotatedVector
        camera.focus_point = self.focusPoint


class DragCameraModeMultiObj(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.landmark_origin = landmarks_at_start.get_point(
            lm.MIDDLE_FINGER_MCP)
        self.camera_origin = camera.location
        self.focus_origin = camera.focus_point
        self.smoothingFactor = 5
        self.prevDxList = [0.0] * self.smoothingFactor
        self.prevDyList = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x_c, y_c, _) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        # proportional to horizontal rotation
        dx = 15 * (x_c - self.landmark_origin[0])
        # proportional to lateral rotation
        dy = 15 * (y_c - self.landmark_origin[1])

        # Kalman filter
        self.prevDxList.append(dx)
        self.prevDxList.pop(0)
        self.prevDyList.append(dy)
        self.prevDyList.pop(0)
        average_dx = sum(self.prevDxList) / self.smoothingFactor
        average_dy = sum(self.prevDyList) / self.smoothingFactor

        gaze = camera.get_gaze_direction()

        up = np.array([0, 0, 1])
        right = np.cross(gaze, up)
        right_norm = right / np.linalg.norm(right)

        new_pos = np.copy(self.camera_origin) + average_dx * right_norm
        new_pos[2] += average_dy

        # Can't go "underground"
        if (new_pos[2] > 0.1):
            camera.location = new_pos
            camera.focus_point = new_pos + gaze


class TiltCameraModeMultiObj(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.tiltOrigin = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.gazeDirectionBeforeTilt = camera.get_gaze_direction()
        self.smoothingFactor = 10
        self.prevDxList = [0.0] * self.smoothingFactor
        self.prevDyList = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x, y, z) = self.tiltOrigin
        (x_c, y_c, z_c) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        dx = 2.5 * (x_c - x)  # proportional to horizontal rotation
        dy = -2.5 * (y_c - y)  # proportional to lateral rotation

        # Kalman filter
        self.prevDxList.append(dx)
        self.prevDxList.pop(0)
        self.prevDyList.append(dy)
        self.prevDyList.pop(0)
        average_dx = sum(self.prevDxList) / self.smoothingFactor
        average_dy = sum(self.prevDyList) / self.smoothingFactor

        camPosVector = camera.location
        gazeDirection = camera.get_gaze_direction()

        axis = np.cross(gazeDirection, np.array([0, 0, 1]))
        gazeDirection = rotate_vector_around_axis(
            self.gazeDirectionBeforeTilt,
            axis,
            average_dy
        )
        gazeDirection = rotate_vector_around_axis(
            gazeDirection, np.array([0, 0, 1]), average_dx)

        newFocusPoint = camPosVector + gazeDirection
        camera.focus_point = newFocusPoint


class ZoomModeFocusShiftMultiObj(CameraMode):
    def set_state(self, landmarks_at_start: Landmarks, camera: Camera3D):
        self.referencePoint = landmarks_at_start.get_point(lm.MIDDLE_FINGER_MCP)
        self.camBeforeTransform = camera.location
        self.smoothingFactor = 5
        self.prevZoomFactors = [0.0] * self.smoothingFactor

    def alter_camera(self, landmarks: Landmarks, camera: Camera3D):
        (x, y, z) = landmarks.get_point(lm.MIDDLE_FINGER_MCP)
        (x_r, y_r, z_r) = self.referencePoint
        zoomFactor = -2 * (x - x_r)

        # Kalman filter
        self.prevZoomFactors.append(zoomFactor)
        self.prevZoomFactors.pop(0)
        averageZoomFactor = sum(self.prevZoomFactors) / self.smoothingFactor

        gazeDirection = camera.get_gaze_direction()
        offset = gazeDirection * averageZoomFactor
        newCamPos = self.camBeforeTransform + offset

        # Can't go "underground"
        if newCamPos[2] > 0.1:
            camera.location = newCamPos
            # Focus shift if not underground
            focus = newCamPos + gazeDirection
            if focus[2] > 0.1:
                camera.focus_point = focus
