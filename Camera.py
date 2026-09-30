import cv2
import mediapipe as mp
import numpy as np
import serial
import struct
ser = serial.Serial('/dev/ttyACM0', 9600)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# Pose landmarks that make up the arms (RIGHT + right: shoulder, elbow, wrist)
ARM_LANDMARKS = {
    mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_ELBOW,
    mp_pose.PoseLandmark.RIGHT_WRIST,
    mp_pose.PoseLandmark.LEFT_WRIST,
}

ARM_CONNECTIONS = {
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
    (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER),
}


def draw_arm_skeleton(image, pose_landmarks, w, h):
    points = {}
    for lm_id in ARM_LANDMARKS:
        lm = pose_landmarks.landmark[lm_id]
        if lm.visibility > 0.5:
            x, y = int(lm.x * w), int(lm.y * h)
            points[lm_id] = (x, y)
            cv2.circle(image, (x, y), 7, (0, 255, 255), -1)
            cv2.circle(image, (x, y), 9, (0, 0, 0), 2)

    for a, b in ARM_CONNECTIONS:
        if a in points and b in points:
            cv2.line(image, points[a], points[b], (0, 255, 255), 3)

def calculate_positions(point1, point2,count):
    result_x = point1.x - point2.x
    result_y = point1.y - point2.y
    angle = np.arctan((result_y/result_x))*180/np.pi
    angle = round(angle,2)
    angle = np.array([count,angle])
    return(angle)

def transmit(i,data):
    data_vector = [i,data]
    payload = struct.pack("<5f", *data_vector)
    print(payload)
    START_MARKER = b"\x02"
    END_MARKER =  b"\x02"
    packet = START_MARKER + payload + END_MARKER
    ser.write(packet)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam. Check your camera index/permissions.")
        return

    with mp_pose.Pose(
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as pose, mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as hands:

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip for a natural mirror view, convert BGR -> RGB for MediaPipe
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            pose_results = pose.process(rgb)
            hand_results = hands.process(rgb)

            rgb.flags.writeable = True
            h, w, _ = frame.shape

            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark

                L_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                L_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
                L_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                R_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                R_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
                R_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
                
                #Thumb controls
                #thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]
                #thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
                #thumb_ip  = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                #thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                
                #Pinky Controls
                #pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
                #pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
                #pinky_dip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP]
                #pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                count = 0
                shoulder_angle = calculate_positions(L_shoulder,L_elbow,count)
                print("shoulder_angle = ")
                transmit(count,shoulder_angle)
                count += 1
                elbow_angle = calculate_positions(L_shoulder,L_wrist,count)
                print("elbow_angle = ")
                transmit(count,elbow_angle)
                #wrist_angle = calculate_positions(thumb_cmc,pinky_mcp)
                #print("wrist_angle = ")
                #transmit(wrist_angle)
                

            # --- Draw arm skeleton (shoulders/elbows/wrists) ---
            if pose_results.pose_landmarks:
                draw_arm_skeleton(frame, pose_results.pose_landmarks, w, h)
            # --- Draw finger skeletons ---
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style(),
                    )

            cv2.imshow("Arm + Finger Skeleton Tracker", frame)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()