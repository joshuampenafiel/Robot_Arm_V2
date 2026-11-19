import numpy as np
import config
bicep = config.BICEP_LENGTH
forearm = config.FOREARM_LENGTH

class KINEMATICS:
    def IK(self, target):
        self.x,self.y,self.z = target
        r = np.hypot(self.x,self.y)
        q1 = np.arctan2(self.y,self.x)
        d = np.hypot(r,self.z)
        if d > bicep + forearm:
            print("too far away ")
            return
        if d < abs(bicep - forearm):
            print("too close")
            return

        cos_D = (forearm**2-d**2+bicep**2)/(2*forearm*bicep)

        q3 = np.pi - np.arccos(np.clip(cos_D, -1, 1))

        # Shoulder: angle between link1 and target direction
        phi = np.arctan2(self.z, r)
        cos_beta = (bicep**2 + d**2 - forearm**2) / (2 * bicep * d)
        beta = np.arccos(np.clip(cos_beta, -1, 1))
        q2 = phi - beta  # elbow-up
        r_fk = bicep*np.cos(q2) + forearm*np.cos(q2 + q3)   
        self.z_fk = bicep*np.sin(q2) + forearm*np.sin(q2 + q3)
        self.x_fk = r_fk*np.cos(q1)
        self.y_fk = r_fk*np.sin(q1)
        print("x:", self.x_fk, "y:", self.y_fk, "z:", self.z_fk)
        return q1, q2, q3

    def check(self):
        if (self.x - config.POS_TOLERANCE <= self.x_fk and 
            self.x_fk <= self.x + config.POS_TOLERANCE and
            self.y - config.POS_TOLERANCE <= self.y_fk and
            self.y_fk <= self.y + config.POS_TOLERANCE and
            self.z - config.POS_TOLERANCE <= self.z_fk and
            self.z_fk <= self.z + config.POS_TOLERANCE):
            return True
        return False