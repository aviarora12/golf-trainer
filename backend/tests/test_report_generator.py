import os

from app.services.report_generator import generate_pdf_report


def test_generate_pdf_report_creates_valid_pdf(tmp_path):
    out = tmp_path / "report.pdf"
    analysis = {
        "spine_angle_setup": 38.2,
        "spine_angle_impact": 33.1,
        "hip_turn": 45.0,
        "x_factor": 52.4,
        "flagged_issues": [
            {"issue": "Early Extension", "severity": "red",
             "description": "Hip extends toward the ball."},
            {"issue": "Sway", "severity": "yellow",
             "description": "Hips move laterally."},
        ],
    }
    path = generate_pdf_report(str(out), "Tiger", analysis)

    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    with open(path, "rb") as f:
        assert f.read(4) == b"%PDF"


def test_generate_pdf_report_handles_no_issues(tmp_path):
    out = tmp_path / "clean.pdf"
    analysis = {"spine_angle_setup": 40.0, "flagged_issues": []}
    path = generate_pdf_report(str(out), "Golfer", analysis)
    assert os.path.getsize(path) > 0


def test_generate_pdf_report_handles_missing_metrics(tmp_path):
    out = tmp_path / "partial.pdf"
    # No numeric metrics -> should render "N/A", not crash
    path = generate_pdf_report(str(out), "Golfer", {"flagged_issues": []})
    assert os.path.getsize(path) > 0
