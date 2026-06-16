"""
AI Pose Analyzer using MediaPipe Pose.
Analyzes exercise form from video frames and provides feedback.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Optional, List, Tuple
import base64


# Define common exercises with their target joint angle ranges
EXERCISE_TEMPLATES = {
    "squat": {
        "name": "深蹲",
        "key_joints": ["left hip", "left knee", "left ankle"],
        "ideal_angles": {
            "down": {"knee": (70, 100), "hip": (70, 100)},
            "up": {"knee": (165, 180), "hip": (160, 180)},
        },
        "common_issues": [
            "膝盖不要超过脚尖",
            "下蹲时保持背部挺直",
            "重心放在脚跟",
        ],
    },
    "push_up": {
        "name": "俯卧撑",
        "key_joints": ["left shoulder", "left elbow", "left wrist"],
        "ideal_angles": {
            "down": {"elbow": (80, 100), "shoulder": (80, 100)},
            "up": {"elbow": (160, 180), "shoulder": (160, 180)},
        },
        "common_issues": [
            "保持身体成一条直线",
            "手臂张开约45度",
            "下降时吸气，起身时呼气",
        ],
    },
    "leg_raise": {
        "name": "腿举",
        "key_joints": ["left hip", "left knee", "left ankle"],
        "ideal_angles": {
            "up": {"hip": (80, 100), "knee": (150, 180)},
            "down": {"hip": (160, 180), "knee": (160, 180)},
        },
        "common_issues": [
            "背部贴紧椅子",
            "控制下降速度",
            "膝盖不要完全伸直锁定",
        ],
    },
    "arm_curl": {
        "name": "臂弯举",
        "key_joints": ["left shoulder", "left elbow", "left wrist"],
        "ideal_angles": {
            "curl": {"elbow": (30, 60)},
            "release": {"elbow": (150, 180)},
        },
        "common_issues": [
            "上臂保持固定",
            "控制动作速度",
            "不要借助惯性",
        ],
    },
}


class PoseAnalyzer:
    """Analyzes human pose from video frames using MediaPipe Pose."""

    def __init__(self):
        """Initialize MediaPipe Pose model."""
        self.detector = None
        try:
            import os
            # Get the directory where pose_analyzer.py is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "pose_landmarker.task")

            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
        except (OSError, Exception) as e:
            print(f"Warning: MediaPipe Pose not available: {e}")
            print("Pose analysis will use rule-based fallback.")
            self.detector = None

        # MediaPipe landmark connections for visualization
        self.POSE_CONNECTIONS = frozenset([
            (0, 1), (1, 2), (2, 3), (3, 7),  # face
            (0, 4), (4, 5), (5, 6), (6, 8),  # face
            (9, 10),  # eyes
            (11, 12),  # shoulders
            (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),  # left arm
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),  # right arm
            (11, 23), (12, 24),  # torso
            (23, 24),  # pelvis
            (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),  # left leg
            (24, 26), (26, 28), (28, 30), (28, 32), (30, 32),  # right leg
        ])

    def analyze_frame(self, image_data: bytes) -> Optional[dict]:
        """
        Analyze a single frame and return pose landmarks.

        Args:
            image_data: Raw image bytes (JPEG/PNG)

        Returns:
            Dictionary with landmarks and angles, or None if no pose detected
        """
        # If detector not available, return None
        if self.detector is None:
            return None

        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return None

            # Convert to RGB (MediaPipe expects RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Create MediaPipe Image
            mp_image = vision.Image(image_format=vision.ImageFormat.SRGB, data=image_rgb)

            # Detect pose
            result = self.detector.detect(mp_image)

            if not result or not result.pose_landmarks:
                return None

            landmarks = result.pose_landmarks[0]

            # Extract key angles
            angles = self._calculate_all_angles(landmarks)

            return {
                "landmarks": landmarks,
                "angles": angles,
                "image_size": (image.shape[1], image.shape[0]),  # (width, height)
            }

        except Exception as e:
            print(f"Pose analysis error: {e}")
            return None

    def analyze_base64_frame(self, base64_data: str) -> Optional[dict]:
        """
        Analyze a base64-encoded frame.

        Args:
            base64_data: Base64-encoded image string (may include data URI prefix)

        Returns:
            Dictionary with landmarks and angles, or None if no pose detected
        """
        # Remove data URI prefix if present
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        try:
            image_data = base64.b64decode(base64_data)
            return self.analyze_frame(image_data)
        except Exception as e:
            print(f"Base64 decode error: {e}")
            return None

    def _calculate_angle(
        self,
        landmark1: Tuple[float, float, float],
        landmark2: Tuple[float, float, float],
        landmark3: Tuple[float, float, float],
    ) -> float:
        """
        Calculate angle at landmark2 formed by landmark1-landmark2-landmark3.
        Returns angle in degrees.
        """
        # Extract coordinates
        p1 = np.array([landmark1.x, landmark1.y])
        p2 = np.array([landmark2.x, landmark2.y])
        p3 = np.array([landmark3.x, landmark3.y])

        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2

        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle) * 180.0 / np.pi

        return float(angle)

    def _calculate_all_angles(self, landmarks) -> dict:
        """Calculate key joint angles from landmarks."""
        angles = {}

        # Define key joint triplets for common exercises
        joint_triplets = {
            # Left side
            "left_knee": (23, 25, 27),       # hip-knee-ankle
            "left_hip": (11, 23, 25),        # shoulder-hip-knee
            "left_elbow": (11, 13, 15),       # shoulder-elbow-wrist
            "left_shoulder": (13, 11, 23),    # elbow-shoulder-hip
            # Right side
            "right_knee": (24, 26, 28),       # hip-knee-ankle
            "right_hip": (12, 24, 26),        # shoulder-hip-knee
            "right_elbow": (12, 14, 16),      # shoulder-elbow-wrist
            "right_shoulder": (14, 12, 24),  # elbow-shoulder-hip
        }

        for joint_name, (idx1, idx2, idx3) in joint_triplets.items():
            try:
                angles[joint_name] = self._calculate_angle(
                    landmarks[idx1], landmarks[idx2], landmarks[idx3]
                )
            except (IndexError, AttributeError):
                angles[joint_name] = None

        return angles

    def evaluate_exercise_form(
        self,
        landmarks,
        angles: dict,
        exercise_type: str,
        phase: str = "down",
    ) -> dict:
        """
        Evaluate exercise form and generate feedback.

        Args:
            landmarks: MediaPipe pose landmarks
            angles: Calculated joint angles
            exercise_type: Type of exercise (squat, push_up, etc.)
            phase: Current phase (up, down, etc.)

        Returns:
            Dictionary with score, feedback, and suggestions
        """
        if exercise_type not in EXERCISE_TEMPLATES:
            exercise_type = "squat"  # Default

        template = EXERCISE_TEMPLATES[exercise_type]
        score = 100
        issues = []
        suggestions = []

        # Check knee angle for squat-type exercises
        if "knee" in angles and angles["knee"]:
            knee_angle = angles["knee"]
            ideal = template.get("ideal_angles", {}).get(phase, {}).get("knee", (0, 180))
            if not (ideal[0] <= knee_angle <= ideal[1]):
                diff = min(abs(knee_angle - ideal[0]), abs(knee_angle - ideal[1]))
                score -= int(diff * 0.5)
                if knee_angle < ideal[0]:
                    issues.append(f"膝盖弯曲角度过小 ({knee_angle:.0f}°)")
                else:
                    issues.append(f"膝盖弯曲角度过大 ({knee_angle:.0f}°)")

        # Check hip angle
        if "hip" in angles and angles["hip"]:
            hip_angle = angles["hip"]
            ideal = template.get("ideal_angles", {}).get(phase, {}).get("hip", (0, 180))
            if not (ideal[0] <= hip_angle <= ideal[1]):
                diff = min(abs(hip_angle - ideal[0]), abs(hip_angle - ideal[1]))
                score -= int(diff * 0.3)
                issues.append(f"髋部角度需要调整 ({hip_angle:.0f}°)")

        # Check elbow angle for arm exercises
        if "elbow" in angles and angles["elbow"]:
            elbow_angle = angles["elbow"]
            ideal = template.get("ideal_angles", {}).get(phase, {}).get("elbow", (0, 180))
            if not (ideal[0] <= elbow_angle <= ideal[1]):
                issues.append(f"肘部角度需要调整 ({elbow_angle:.0f}°)")

        # Check for common issues based on alignment
        if landmarks:
            # Check shoulder alignment (for push-up type exercises)
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            if hasattr(left_shoulder, 'x') and hasattr(right_shoulder, 'x'):
                shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
                if shoulder_diff > 0.05:  # More than 5% height difference
                    suggestions.append("双肩保持水平")

            # Check hip alignment
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            if hasattr(left_hip, 'x') and hasattr(right_hip, 'x'):
                hip_diff = abs(left_hip.y - right_hip.y)
                if hip_diff > 0.05:
                    suggestions.append("臀部保持水平，不要歪斜")

        # Clamp score
        score = max(0, min(100, score))

        # Add common suggestions if score is low
        if score < 70:
            suggestions.extend(template["common_issues"][:2])
        elif score < 90:
            suggestions.append(template["common_issues"][0] if template["common_issues"] else "保持当前姿势")

        # Generate feedback text
        if score >= 90:
            feedback = f"动作标准！继续保持 ({score}分)"
        elif score >= 70:
            feedback = f"动作基本正确，有小细节需注意 ({score}分)"
        else:
            feedback = f"需要改进：{'；'.join(issues[:2]) if issues else '请咨询教练'} ({score}分)"

        return {
            "score": score,
            "feedback": feedback,
            "issues": issues,
            "suggestions": suggestions[:3],  # Limit to 3 suggestions
            "angles": {k: round(v, 1) if v else None for k, v in angles.items()},
        }

    def close(self):
        """Clean up resources."""
        if self.detector:
            self.detector.close()


# Global pose analyzer instance (lazy initialization)
_pose_analyzer: Optional[PoseAnalyzer] = None


def get_pose_analyzer() -> PoseAnalyzer:
    """Get or create the global pose analyzer instance."""
    global _pose_analyzer
    if _pose_analyzer is None:
        _pose_analyzer = PoseAnalyzer()
    return _pose_analyzer


def analyze_exercise_frame(
    base64_frame: str,
    exercise_type: str = "squat",
    phase: str = "down",
) -> dict:
    """
    Convenience function to analyze a single exercise frame.

    Args:
        base64_frame: Base64-encoded video frame
        exercise_type: Type of exercise
        phase: Current exercise phase

    Returns:
        Analysis result with score, feedback, and suggestions
    """
    # If no frame provided or MediaPipe not available, return default feedback
    if not base64_frame:
        return _get_default_feedback(exercise_type)

    analyzer = get_pose_analyzer()
    result = analyzer.analyze_base64_frame(base64_frame)

    if not result:
        # MediaPipe not available or no pose detected
        # Return default feedback based on exercise type
        return _get_default_feedback(exercise_type)

    return analyzer.evaluate_exercise_form(
        result["landmarks"],
        result["angles"],
        exercise_type,
        phase,
    )


def _get_default_feedback(exercise_type: str) -> dict:
    """Get default feedback when MediaPipe is not available."""
    feedbacks = {
        "squat": {
            "score": 75,
            "feedback": "深蹲动作基本标准，膝盖不要超过脚尖",
            "suggestions": [
                "保持核心收紧",
                "下蹲时膝盖对准第二脚趾方向",
                "起身时用脚跟发力",
            ],
            "angles": {},
        },
        "push_up": {
            "score": 75,
            "feedback": "俯卧撑动作基本正确，身体保持一条直线",
            "suggestions": [
                "手臂张开约45度",
                "下降时吸气，起身时呼气",
                "保持核心收紧",
            ],
            "angles": {},
        },
        "leg_raise": {
            "score": 75,
            "feedback": "腿举动作基本标准，背部贴紧椅子",
            "suggestions": [
                "控制下降速度",
                "膝盖不要完全伸直锁定",
                "用腹部力量抬起双腿",
            ],
            "angles": {},
        },
        "arm_curl": {
            "score": 75,
            "feedback": "臂弯举动作基本正确，上臂保持固定",
            "suggestions": [
                "控制动作速度",
                "不要借助惯性",
                "专注于肱二头肌发力",
            ],
            "angles": {},
        },
    }
    return feedbacks.get(exercise_type, feedbacks["squat"])
