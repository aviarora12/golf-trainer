import cv2
import numpy as np
from typing import List, Dict
import subprocess


class VideoProcessor:

    @staticmethod
    def extract_frames(video_path: str, target_fps: int = 30) -> List[np.ndarray]:
        """Extract frames from video at target FPS. Returns list of numpy arrays (BGR, H×W×3)."""
        cap = cv2.VideoCapture(video_path)
        source_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(source_fps / target_fps))

        frames = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frames.append(frame)

            frame_count += 1

        cap.release()
        return frames

    @staticmethod
    def detect_video_quality(video_path: str) -> Dict:
        """Validate video: resolution, fps, duration, brightness."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / (fps + 0.001)

        errors = []
        if fps < 30:
            errors.append(f"Frame rate too low: {fps:.1f} fps (need 30+)")
        if duration < 5 or duration > 15:
            errors.append(f"Duration {duration:.1f}s (need 5-15s)")
        if width < 720 or height < 480:
            errors.append(f"Resolution {width}x{height} (need 720p+)")

        # Check brightness
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_intensity = gray.mean()
            if mean_intensity < 30:
                errors.append("Video too dark (film in daylight)")

        cap.release()

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "fps": fps,
            "duration": duration,
            "resolution": f"{width}x{height}"
        }

    @staticmethod
    def compress_video(input_path: str, output_path: str) -> None:
        """Compress video: H.264, 720p, 30 fps, ~5 Mbps."""
        cmd = [
            "ffmpeg", "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-s", "1280x720",
            "-r", "30",
            "-b:v", "5000k",
            "-acodec", "aac",
            "-b:a", "128k",
            "-y", output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    @staticmethod
    def extract_key_frames(frames: List[np.ndarray]) -> Dict:
        """Extract frames at P1, P2, P4, P7, P10 positions."""
        total = len(frames)
        positions = {
            'P1': int(0 * total / 10),
            'P2': int(1 * total / 10),
            'P4': int(4 * total / 10),
            'P7': int(7 * total / 10),
            'P10': int(9 * total / 10),
        }

        return {pos: frames[idx] if idx < total else frames[-1]
                for pos, idx in positions.items()}
