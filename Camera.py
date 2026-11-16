import cv2
import mediapipe as mp
import numpy as np
import serial
import time
ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
ser.reset_input_buffer()
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

max_angle = 180
min_angle = 0
angle_tolerance = 2
data = []
last_pos = [90,90,90,90]

bicep_length = 1
forearm_length = 1

TRANSMISSION_COUNTER = 0
ARM_LANDMARKS = {
    #mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    #mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_ELBOW,
    #mp_pose.PoseLandmark.RIGHT_WRIST,
    mp_pose.PoseLandmark.LEFT_WRIST,
}

ARM_CONNECTIONS = {
    #(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
    #(mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    #(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER),
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

def transmit(data):
    global TRANSMISSION_COUNTER
    global last_pos
    if TRANSMISSION_COUNTER != 3:
        data.append(last_pos[2])
        data.append(last_pos[3])
    ser.write((",".join(str(int(v)) for v in data) + "\n").encode())
    TRANSMISSION_COUNTER = 0
    last_pos = list(data)
    data.clear()
    return

def add_data(q1,q2,q3):
    data.append(float(q1))
    data.append(float(q2))
    data.append(float(q3))
    global TRANSMISSION_COUNTER
    TRANSMISSION_COUNTER += 1
    return 

def IK(bicep,forearm,target):
    x,y,z = target

    r = np.hypot(x,y)
    q1 = np.arctan2(y,x)
    d = np.hypot(r,z)
    if d > bicep + forearm:
        print("too far away ")
        return
    if d< abs(bicep - forearm):
        print("too close")
        return

    cos_D = (forearm**2-d**2+bicep**2)/(2*forearm*bicep)

    q3 = np.pi - np.arccos(np.clip(cos_D, -1, 1))

    # Shoulder: angle between link1 and target direction
    phi = np.arctan2(z, r)
    cos_beta = (bicep**2 + d**2 - forearm**2) / (2 * bicep * d)
    beta = np.arccos(np.clip(cos_beta, -1, 1))
    q2 = phi - beta  # elbow-up


    r_fk = bicep*np.cos(q2) + forearm*np.cos(q2 + q3)   
    z_fk = bicep*np.sin(q2) + forearm*np.sin(q2 + q3)
    x_fk = r_fk*np.cos(q1)
    y_fk = r_fk*np.sin(q1)
    print("x:", x_fk, "y:", y_fk, "z:", z_fk)
    return q1, q2, q3

def main():
    global data
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

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            pose_results = pose.process(rgb)
            hand_results = hands.process(rgb)
            rgb.flags.writeable = True
            h, w, _ = frame.shape

            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                R_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

                target = R_wrist
                q1,q2,q3 = IK(bicep_length,forearm_length,target)
                add_data(q1,q2,q3)

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

                thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
                    
                wrist_angle = calculate_positions(pinky_mcp,thumb_cmc)
                claw_angle = calculate_positions(pinky_mcp,thumb_tip)
                add_data(wrist_angle,claw_angle)
            
            transmit(data)

            cv2.imshow("Arm + Finger Skeleton Tracker", frame)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

            while ser.in_waiting:
                reply = ser.readline().decode('utf-8', errors='ignore').strip()
                if reply:
                    #print("Arduino says:", data)
                    pass
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()