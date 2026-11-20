import config
import time
import serial


class ARDUINO:
    def __init__(self):
            self.ser = serial.Serial(config.SERIAL_PORT, config.BAUD_RATE)
            time.sleep(config.SERIAL_STARTUP_DELAY)
            self.TRANSMISSION_COUNTER = 0
            self.data = []
            self.last_pos = [config.HOME_POS]
            return

    def add_data(self,q1,q2,q3,hand_check):
        self.data=[]
        self.data=[float(q1),float(q2),float(q3),bool(hand_check)]
        return 

    def transmit(self):
        if len(self.data) < 3:
            self.data.extend(self.last_pos[len(self.data):])
        self.ser.write((",".join(str(int(v)) for v in self.data) + "\n").encode())
        self.last_pos = list(self.data)
        self.data = []
        return