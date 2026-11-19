import cv2
import mediapipe as mp
import config
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hand = mp.solutions.hands


class CAMERA:
    ARM_LANDMARKS = {
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_ELBOW,
    mp_pose.PoseLandmark.LEFT_WRIST,
    }
    ARM_CONNECTIONS = {
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
}

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Camera could not be opened")
        self.pose = mp.solutions.pose.Pose(
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        ) 
        self.hand = mp.solutions.hands.Hands(
        max_num_hands=config.MAX_NUM_HANDS,
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
    )  

    def read(self):
        success,frame = self.cap.read()
        if not success:
            return None
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        self.h, self.w, _ = frame.shape

        pose_results = self.pose.process(rgb)
        hand_results = self.hand.process(rgb)
        return frame, pose_results.pose_landmarks, hand_results.multi_hand_landmarks
    
    def close(self):
        self.cap.release()
        self.pose.close()
        self.hands.close()
        return
    
    def draw_arm_skeleton(self, image, pose_landmarks):
        points = {}
        for lm_id in self.ARM_LANDMARKS:
            lm = pose_landmarks.landmark[lm_id]
            if lm.visibility > 0.5:
                x, y = int(lm.x * self.w), int(lm.y * self.h)
                points[lm_id] = (x, y)
                cv2.circle(image, (x, y), 7, (0, 255, 255), -1)
                cv2.circle(image, (x, y), 9, (0, 0, 0), 2)

        for a, b in self.ARM_CONNECTIONS:
            if a in points and b in points:
                cv2.line(image, points[a], points[b], (0, 255, 255), 3)

    def draw_hand_skeleton(self, frame, hand_landmarks_list):
        if not hand_landmarks_list:
            return
        for hand_landmarks in hand_landmarks_list:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hand.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style(),
            )

    def quit_check(self):
        if cv2.waitKey(5) & 0xFF == ord('q'):
            return True
        return False