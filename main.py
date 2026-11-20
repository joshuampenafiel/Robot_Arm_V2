import communications
import kinematics
import camera
import cv2
cam = camera.CAMERA()
serial = communications.ARDUINO()
kin = kinematics.KINEMATICS()

#CAMERA INITALIZE -> 

cam
serial

# Loop begins
while 1:

# CAMERA OBSERVE  

    result = cam.read()
    if result == None:
        print("no camera")
        continue
    frame, arm_pose,hand_pose = result

# Draw DATA POINTS -> 
    print("DRAW DATA POINTS")
    cam.draw_arm_skeleton(frame,arm_pose)
    hand_in_frame = cam.draw_hand_skeleton(frame,hand_pose)
    cv2.imshow("frame", frame)   
    target = cam.target()

# INVERSE KINEMATICS -> 
    print("INVERSE KINEMATICS")
    q1,q2,q3 = kin.IK(target)

# Hand Check

    print("HAND CHECK")
    hand_check = False
    if hand_in_frame == True:
        print("    hand in frame")
        hand_check = cam.hand_check()

# SANITY CHECK(FORWARDS KINEMATICS)

    print("SANITY CHECK")
    kin_check = kin.check()

# SEND TO ARDUINO
    print("TRANSMIT DATA")
    if kin_check == True:
        serial.add_data(q1,q2,q3,hand_check)
        serial.transmit

# Loop ends
    quit = cam.quit_check()
    if quit == True:
        print("QUITTING")
        break
# Close Camera
cam.close()