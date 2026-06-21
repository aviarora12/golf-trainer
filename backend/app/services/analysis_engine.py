import numpy as np
from typing import List, Dict, Tuple


class AnalysisEngine:

    @staticmethod
    def xyz_from_landmark(landmark: Dict) -> np.ndarray:
        """Convert landmark dict to (x, y, z) numpy array."""
        return np.array([landmark['x'], landmark['y'], landmark['z']])

    @staticmethod
    def compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Compute angle at p2 formed by p1-p2-p3 (degrees, 0-180)."""
        v1 = p1 - p2
        v2 = p3 - p2
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_angle)))

    def get_landmark_xyz(self, landmarks: List[Dict], index: int) -> np.ndarray:
        """Get landmark (x, y, z) by index."""
        lm = next((l for l in landmarks if l['index'] == index), None)
        return self.xyz_from_landmark(lm) if lm else np.array([0.0, 0.0, 0.0])

    def compute_spine_angle(self, landmarks: List[Dict]) -> float:
        """Spine angle (forward bend): angle between spine vector and vertical."""
        # Neck (~0), left_hip (23), right_hip (24)
        neck = self.get_landmark_xyz(landmarks, 0)
        left_hip = self.get_landmark_xyz(landmarks, 23)
        right_hip = self.get_landmark_xyz(landmarks, 24)
        mid_hip = (left_hip + right_hip) / 2

        vertical = np.array([0.0, -1.0, 0.0])

        angle = self.compute_angle(mid_hip, neck, neck + vertical)
        return float(angle)

    def compute_hip_shoulder_angles(self, landmarks: List[Dict]) -> Tuple[float, float, float]:
        """Compute hip turn, shoulder turn, and X-Factor (separation)."""
        left_shoulder = self.get_landmark_xyz(landmarks, 11)
        right_shoulder = self.get_landmark_xyz(landmarks, 12)
        left_hip = self.get_landmark_xyz(landmarks, 23)
        right_hip = self.get_landmark_xyz(landmarks, 24)

        # Axial rotation: angle in horizontal plane (x-z)
        hip_vec = right_hip - left_hip
        shoulder_vec = right_shoulder - left_shoulder

        hip_angle = float(np.degrees(np.arctan2(hip_vec[0], hip_vec[2])))
        shoulder_angle = float(np.degrees(np.arctan2(shoulder_vec[0], shoulder_vec[2])))

        x_factor = abs(shoulder_angle - hip_angle)

        return (hip_angle, shoulder_angle, x_factor)

    def detect_early_extension(self, landmarks_setup: List[Dict], landmarks_impact: List[Dict]) -> bool:
        """Detect early extension: hip rises >2 inches from setup to impact."""
        left_hip_setup = self.get_landmark_xyz(landmarks_setup, 23)
        right_hip_setup = self.get_landmark_xyz(landmarks_setup, 24)
        mid_hip_setup_y = (left_hip_setup[1] + right_hip_setup[1]) / 2

        left_hip_impact = self.get_landmark_xyz(landmarks_impact, 23)
        right_hip_impact = self.get_landmark_xyz(landmarks_impact, 24)
        mid_hip_impact_y = (left_hip_impact[1] + right_hip_impact[1]) / 2

        hip_rise = mid_hip_setup_y - mid_hip_impact_y
        return bool(hip_rise > 0.05)  # 5% of frame height

    def detect_reverse_pivot(self, landmarks_setup: List[Dict], landmarks_top: List[Dict]) -> bool:
        """Detect reverse pivot: spine tilt toward target at top."""
        left_shoulder_setup = self.get_landmark_xyz(landmarks_setup, 11)
        right_shoulder_setup = self.get_landmark_xyz(landmarks_setup, 12)
        mid_setup_x = (left_shoulder_setup[0] + right_shoulder_setup[0]) / 2

        left_shoulder_top = self.get_landmark_xyz(landmarks_top, 11)
        right_shoulder_top = self.get_landmark_xyz(landmarks_top, 12)
        mid_top_x = (left_shoulder_top[0] + right_shoulder_top[0]) / 2

        lateral_shift = mid_top_x - mid_setup_x
        return bool(lateral_shift > 0.03)  # 3% toward target

    def detect_casting(self, landmarks: List[Dict]) -> bool:
        """Detect casting: lag angle < 60° at mid-downswing."""
        left_wrist = self.get_landmark_xyz(landmarks, 15)
        left_elbow = self.get_landmark_xyz(landmarks, 13)

        arm_vec = left_wrist - left_elbow
        shaft_vec = np.array([arm_vec[1], -arm_vec[0], arm_vec[2]])

        lag_angle = self.compute_angle(left_elbow, left_wrist, left_wrist + shaft_vec)
        return bool(lag_angle < 60)

    def detect_sway(self, landmarks_backswing: List[Dict]) -> bool:
        """Detect sway: hip lateral movement > 1 hip-width."""
        left_hip = self.get_landmark_xyz(landmarks_backswing, 23)
        right_hip = self.get_landmark_xyz(landmarks_backswing, 24)
        hip_width = abs(right_hip[0] - left_hip[0])
        return bool(hip_width > 0.20)  # Threshold

    def detect_camera_angle(self, landmarks: List[Dict]) -> str:
        """Detect down-the-line vs face-on."""
        left_shoulder = self.get_landmark_xyz(landmarks, 11)
        right_shoulder = self.get_landmark_xyz(landmarks, 12)
        left_hip = self.get_landmark_xyz(landmarks, 23)
        right_hip = self.get_landmark_xyz(landmarks, 24)

        shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
        hip_width = abs(right_hip[0] - left_hip[0])

        ratio = shoulder_width / (hip_width + 1e-6)
        return "down-the-line" if ratio < 0.85 else "face-on"

    def generate_flagged_issues(self, flags: Dict) -> List[Dict]:
        """Generate human-readable issue descriptions."""
        issues = []

        if flags.get('early_extension'):
            issues.append({
                'issue': 'Early Extension',
                'severity': 'red',
                'description': 'Your hip is extending toward the ball in the downswing.',
                'explanation': 'This causes your spine to come up early, leading to blocks and inconsistent contact.',
                'drills': ['drill_early_ext_1', 'drill_early_ext_2']
            })

        if flags.get('reverse_pivot'):
            issues.append({
                'issue': 'Reverse Pivot',
                'severity': 'yellow',
                'description': 'Your weight is shifting toward the target at the top of the backswing.',
                'explanation': 'This reduces power and causes inconsistent ballstriking.',
                'drills': ['drill_pivot_1']
            })

        if flags.get('casting'):
            issues.append({
                'issue': 'Casting',
                'severity': 'red',
                'description': 'You are releasing the club too early in the downswing.',
                'explanation': 'The club races ahead of your hands and decelerates before impact, reducing distance.',
                'drills': ['drill_lag_1', 'drill_lag_2']
            })

        if flags.get('sway'):
            issues.append({
                'issue': 'Sway',
                'severity': 'yellow',
                'description': 'Your hips are moving laterally instead of rotating.',
                'explanation': 'This causes inconsistent contact and loss of power.',
                'drills': ['drill_sway_1']
            })

        return issues
