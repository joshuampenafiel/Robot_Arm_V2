import serial, time, threading
from evdev import InputDevice, ecodes

ser = serial.Serial('/dev/ttyACM0', 9600)
dev = InputDevice('/dev/input/event3')
held = set()

def key_listener():
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                held.add(event.code)
            elif event.value == 0:
                held.discard(event.code)

threading.Thread(target=key_listener, daemon=True).start()

# Map keys to commands
key_map = {
    ecodes.KEY_Q: b"q\n",   # + Shoulder Angle
    ecodes.KEY_W: b"w\n",   # - Shoulder Angle
    ecodes.KEY_A: b"a\n",   # + Elbow Angle
    ecodes.KEY_S: b"s\n",   # - Elbow Angle
    ecodes.KEY_Z: b"z\n",   # CW Wrist
    ecodes.KEY_X: b"x\n",   # CCW wrist
  
    ecodes.KEY_SPACE: b'\n',  # grip/close
}

while True:
    for key, cmd in key_map.items():
        if key in held:
            ser.write(cmd)
            print(cmd, "sent\n")
    time.sleep(0.01)   