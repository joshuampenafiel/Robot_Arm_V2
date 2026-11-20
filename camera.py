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
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE)
        self.hand_landmarks = None
        return

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
        self.hand.close()
        return
    
    def draw_arm_skeleton(self, image, pose_landmarks):
        points = {}
        for lm_id in self.ARM_LANDMARKS:
            self.lm = pose_landmarks.landmark[lm_id]
            if self.lm.visibility > 0.5:
                x, y = int(self.lm.x * self.w), int(self.lm.y * self.h)
                points[lm_id] = (x, y)
                cv2.circle(image, (x, y), 7, (0, 255, 255), -1)
                cv2.circle(image, (x, y), 9, (0, 0, 0), 2)

        for a, b in self.ARM_CONNECTIONS:
            if a in points and b in points:
                cv2.line(image, points[a], points[b], (0, 255, 255), 3)
        
    def target(self):
        return self.lm.x,self.lm.y,self.lm.z

    def draw_hand_skeleton(self, frame, hand_landmarks_list):
        self.hand_landmarks = None   
        if not hand_landmarks_list:
            return
        for self.hand_landmarks in hand_landmarks_list:
            mp_drawing.draw_landmarks(
                frame,
                self.hand_landmarks,
                mp_hand.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
#        print("thumb_tip = ",self.thumb_tip,"\n")
#        print("pinky_mcp = ",self.thumb_tip,"\n")

    def quit_check(self):
        if cv2.waitKey(5) & 0xFF == ord('q'):
            return True
        return False    

    def hand_check(self):
        #thumb_cmc = self.hand_landmarks.landmark[mp_hand.HandLandmark.THUMB_CMC]
        thumb_tip = self.hand_landmarks.landmark[mp_hand.HandLandmark.THUMB_TIP]
        pinky_mcp = self.hand_landmarks.landmark[mp_hand.HandLandmark.PINKY_MCP]
        x_check = thumb_tip.x - pinky_mcp.x
        y_check = thumb_tip.y - pinky_mcp.y
        z_check = thumb_tip.z - pinky_mcp.z
        print("The x_check is",x_check)
        print("The y_check is",y_check)
        print("The z_check is",z_check)

        if (abs(x_check) <= config.HAND_TOL and
            abs(y_check) <= config.HAND_TOL and
            abs(z_check) <= config.HAND_TOL):
            print("close hand")
            return True
        return False
    