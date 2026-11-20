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
    
    cam.draw_arm_skeleton(frame,arm_pose)
    cam.draw_hand_skeleton(frame,hand_pose)
    cv2.imshow("frame", frame)   
    target = cam.target()
#    print("target is ", target)
# INVERSE KINEMATICS -> 

    q1,q2,q3 = kin.IK(target)

# Hand Check

    cam.hand_check()

# SANITY CHECK(FORWARDS KINEMATICS)

    check = kin.check()

# SEND TO ARDUINO

    serial.add_data(q1,q2,q3)
    serial.transmit

# Loop ends
    quit = cam.quit_check()
    if quit == True:
        break
# Close Camera
cam.close()