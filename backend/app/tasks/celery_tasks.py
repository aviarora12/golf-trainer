from celery import Celery
import os
import tempfile
from datetime import datetime

from app.database import SessionLocal
from app.models import Swing, SwingAnalysis
from app.services.video_processor import VideoProcessor
from app.services.pose_detector import PoseDetector
from app.services.analysis_engine import AnalysisEngine
from app.services.s3_service import s3_service
from app.services.report_generator import generate_pdf_report

celery_app = Celery(
    'swingcheck',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)


@celery_app.task(bind=True)
def process_swing_video(self, swing_id: str, s3_url: str):
    """Main async task: download, analyze, generate report."""
    db = SessionLocal()
    swing = None

    try:
        swing = db.query(Swing).filter(Swing.id == swing_id).first()
        if not swing:
            return {"error": "Swing not found"}

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Download video
            video_path = f"{tmpdir}/input.mp4"
            s3_key = s3_url.split('.amazonaws.com/')[-1]
            s3_service.download_file(s3_key, video_path)

            # 2. Extract frames
            vp = VideoProcessor()
            frames = vp.extract_frames(video_path, target_fps=30)
            if not frames:
                raise ValueError("No frames could be extracted from the video")

            # 3. Detect landmarks
            pd = PoseDetector()
            all_landmarks = pd.detect_landmarks_from_frames(frames)
            n = len(all_landmarks)

            # Get landmarks at key positions
            p1_landmarks = all_landmarks[0]['landmarks'] if n > 0 else []
            p4_landmarks = all_landmarks[n // 2]['landmarks'] if n > 1 else p1_landmarks
            p7_landmarks = all_landmarks[int(7 * n / 10)]['landmarks'] if n > 1 else p1_landmarks

            # 4. Compute angles & detect flags
            ae = AnalysisEngine()
            spine_setup = ae.compute_spine_angle(p1_landmarks)
            spine_impact = ae.compute_spine_angle(p7_landmarks)
            hip_turn, shoulder_turn, x_factor = ae.compute_hip_shoulder_angles(p4_landmarks)

            flags = {
                'early_extension': ae.detect_early_extension(p1_landmarks, p7_landmarks),
                'reverse_pivot': ae.detect_reverse_pivot(p1_landmarks, p4_landmarks),
                'sway': ae.detect_sway(p4_landmarks),
                'casting': ae.detect_casting(p4_landmarks),
            }

            flagged_issues = ae.generate_flagged_issues(flags)
            camera_angle = ae.detect_camera_angle(p1_landmarks)

            # 5. Generate PDF
            pdf_path = f"{tmpdir}/report.pdf"
            generate_pdf_report(pdf_path, swing.user.profile_name or "Golfer", {
                'spine_angle_setup': spine_setup,
                'spine_angle_impact': spine_impact,
                'hip_turn': hip_turn,
                'x_factor': x_factor,
                'flagged_issues': flagged_issues
            })

            # 6. Upload PDF to S3
            pdf_s3_key = f"reports/{swing_id}/report.pdf"
            with open(pdf_path, 'rb') as f:
                pdf_url = s3_service.upload_file(f, pdf_s3_key)

            # 7. Update database
            analysis = SwingAnalysis(
                swing_id=swing_id,
                spine_angle_setup_deg=spine_setup,
                spine_angle_impact_deg=spine_impact,
                hip_turn_top_deg=hip_turn,
                shoulder_turn_top_deg=shoulder_turn,
                x_factor_deg=x_factor,
                early_extension_flag=flags['early_extension'],
                reverse_pivot_flag=flags['reverse_pivot'],
                sway_flag=flags['sway'],
                casting_flag=flags['casting'],
                flagged_issues=flagged_issues,
                detected_camera_angle=camera_angle,
                confidence_score=0.85
            )
            db.add(analysis)
            swing.analysis_status = 'complete'
            swing.report_pdf_url = pdf_url
            swing.processed_at = datetime.utcnow()
            swing.analysis_json = {
                'spine_setup': spine_setup,
                'spine_impact': spine_impact,
                'hip_turn': hip_turn,
                'x_factor': x_factor,
                'flags': flags
            }
            db.commit()

        return {"swing_id": swing_id, "status": "complete"}

    except Exception as e:
        if swing is not None:
            swing.analysis_status = 'failed'
            swing.error_message = str(e)
            db.commit()
        return {"swing_id": swing_id, "status": "failed", "error": str(e)}

    finally:
        db.close()
