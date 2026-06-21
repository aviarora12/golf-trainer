import mediapipe as mp
import numpy as np
import cv2
from typing import List, Dict


class PoseDetector:

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            smooth_landmarks=False
        )
        self.landmark_names = {
            0: 'nose', 2: 'left_eye', 5: 'right_eye',
            11: 'left_shoulder', 12: 'right_shoulder',
            13: 'left_elbow', 14: 'right_elbow',
            15: 'left_wrist', 16: 'right_wrist',
            23: 'left_hip', 24: 'right_hip',
            25: 'left_knee', 26: 'right_knee',
            27: 'left_ankle', 28: 'right_ankle',
        }

    def detect_landmarks(self, frame: np.ndarray) -> Dict:
        """Detect 33 pose landmarks from a single frame."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        if not results.pose_landmarks:
            return {"landmarks": [], "success": False}

        landmarks = []
        for i, lm in enumerate(results.pose_landmarks.landmark):
            landmarks.append({
                "index": i,
                "name": self.landmark_names.get(i, f"landmark_{i}"),
                "x": float(lm.x),
                "y": float(lm.y),
                "z": float(lm.z),
                "confidence": float(lm.visibility)
            })

        return {"landmarks": landmarks, "success": True}

    def detect_landmarks_from_frames(self, frames: List[np.ndarray]) -> List[Dict]:
        """Detect landmarks for multiple frames."""
        results = []
        for idx, frame in enumerate(frames):
            lm_result = self.detect_landmarks(frame)
            lm_result['frame_idx'] = idx
            results.append(lm_result)
        return results

    def get_landmark(self, landmarks: List[Dict], index_or_name) -> Dict:
        """Get landmark by index or name."""
        if isinstance(index_or_name, int):
            return next((lm for lm in landmarks if lm['index'] == index_or_name), None)
        else:
            return next((lm for lm in landmarks if lm['name'] == index_or_name), None)
