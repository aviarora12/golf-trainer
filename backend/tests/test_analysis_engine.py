import numpy as np
import pytest

from app.services.analysis_engine import AnalysisEngine
from tests.helpers import make_landmarks

# Landmark indices
NOSE, L_SH, R_SH, L_EL, L_WR, L_HIP, R_HIP = 0, 11, 12, 13, 15, 23, 24


@pytest.fixture
def ae():
    return AnalysisEngine()


def test_compute_angle_right_angle(ae):
    p1 = np.array([1.0, 0.0, 0.0])
    p2 = np.array([0.0, 0.0, 0.0])
    p3 = np.array([0.0, 1.0, 0.0])
    assert ae.compute_angle(p1, p2, p3) == pytest.approx(90.0, abs=1e-3)


def test_compute_angle_straight_line(ae):
    p1 = np.array([-1.0, 0.0, 0.0])
    p2 = np.array([0.0, 0.0, 0.0])
    p3 = np.array([1.0, 0.0, 0.0])
    # Engine adds a 1e-6 epsilon to avoid div-by-zero, so 180° lands within ~0.1°
    assert ae.compute_angle(p1, p2, p3) == pytest.approx(180.0, abs=0.2)


def test_get_landmark_xyz_missing_returns_zeros(ae):
    # Empty list -> default zero vector, no crash
    assert np.allclose(ae.get_landmark_xyz([], 23), np.array([0.0, 0.0, 0.0]))


def test_spine_angle_is_finite(ae):
    lms = make_landmarks({NOSE: (0.5, 0.1, 0.0), L_HIP: (0.45, 0.6, 0.0), R_HIP: (0.55, 0.6, 0.0)})
    angle = ae.compute_spine_angle(lms)
    assert 0.0 <= angle <= 180.0


def test_early_extension_triggers_on_hip_rise(ae):
    setup = make_landmarks({L_HIP: (0.45, 0.60, 0.0), R_HIP: (0.55, 0.60, 0.0)})
    impact = make_landmarks({L_HIP: (0.45, 0.48, 0.0), R_HIP: (0.55, 0.48, 0.0)})  # hips rise 0.12
    assert ae.detect_early_extension(setup, impact) is True


def test_early_extension_not_triggered_when_stable(ae):
    setup = make_landmarks({L_HIP: (0.45, 0.60, 0.0), R_HIP: (0.55, 0.60, 0.0)})
    impact = make_landmarks({L_HIP: (0.45, 0.59, 0.0), R_HIP: (0.55, 0.59, 0.0)})  # 0.01 rise
    assert ae.detect_early_extension(setup, impact) is False


def test_reverse_pivot_triggers_on_target_shift(ae):
    setup = make_landmarks({L_SH: (0.45, 0.2, 0.0), R_SH: (0.55, 0.2, 0.0)})       # mid x 0.50
    top = make_landmarks({L_SH: (0.50, 0.2, 0.0), R_SH: (0.60, 0.2, 0.0)})         # mid x 0.55 (+0.05)
    assert ae.detect_reverse_pivot(setup, top) is True


def test_sway_threshold(ae):
    swayed = make_landmarks({L_HIP: (0.30, 0.6, 0.0), R_HIP: (0.55, 0.6, 0.0)})    # width 0.25
    stable = make_landmarks({L_HIP: (0.45, 0.6, 0.0), R_HIP: (0.55, 0.6, 0.0)})    # width 0.10
    assert ae.detect_sway(swayed) is True
    assert ae.detect_sway(stable) is False


def test_detect_camera_angle(ae):
    # Narrow shoulders relative to hips -> down-the-line
    dtl = make_landmarks({
        L_SH: (0.49, 0.2, 0.0), R_SH: (0.51, 0.2, 0.0),   # width 0.02
        L_HIP: (0.40, 0.6, 0.0), R_HIP: (0.60, 0.6, 0.0),  # width 0.20
    })
    assert ae.detect_camera_angle(dtl) == "down-the-line"

    face_on = make_landmarks({
        L_SH: (0.35, 0.2, 0.0), R_SH: (0.65, 0.2, 0.0),    # width 0.30
        L_HIP: (0.40, 0.6, 0.0), R_HIP: (0.60, 0.6, 0.0),  # width 0.20
    })
    assert ae.detect_camera_angle(face_on) == "face-on"


def test_hip_shoulder_x_factor_non_negative(ae):
    lms = make_landmarks({
        L_SH: (0.4, 0.2, 0.1), R_SH: (0.6, 0.2, -0.1),
        L_HIP: (0.45, 0.6, 0.05), R_HIP: (0.55, 0.6, -0.05),
    })
    hip, shoulder, x_factor = ae.compute_hip_shoulder_angles(lms)
    assert x_factor >= 0.0


def test_generate_flagged_issues_shapes(ae):
    flags = {"early_extension": True, "casting": True, "reverse_pivot": False, "sway": False}
    issues = ae.generate_flagged_issues(flags)
    names = {i["issue"] for i in issues}
    assert names == {"Early Extension", "Casting"}
    for issue in issues:
        assert issue["severity"] in {"red", "yellow", "green"}
        assert isinstance(issue["drills"], list)
