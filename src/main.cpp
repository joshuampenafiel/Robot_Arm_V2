#include <Arduino.h>
#include <Servo.h>

class MOTOR {
  private:
    Servo servo;
    int pin;
    int angle;

  public:
    MOTOR(int pin, int startAngle = 0) {
        this->pin = pin;
        angle = startAngle;
    }

    void begin() {
        servo.attach(pin);
        servo.write(angle);
    }

    void set_angle(int reading) {
      angle = compare(reading);  
      servo.write(angle);
    }
    int compare(int reading){
      if (reading - 10 > 0 && angle < 180) {
        angle++;
        }
      else if (reading + 10 < 0 && angle > 0) {
        angle--;
      }
      return angle;
    }
};

class ARM {
  private:
    MOTOR shoulder, elbow, wrist, claw;
  public:
    ARM(int (sPin), int (ePin), int (wPin), int(cPin)):shoulder(sPin), elbow(ePin),wrist(wPin),claw(cPin){}
    void begin(){
      shoulder.begin();
      elbow.begin();
      wrist.begin();
      claw.begin();
  }
    bool receive() {
        if (!Serial.available()) return false;
        String line = Serial.readStringUntil('\n');

        int c1 = line.indexOf(',');
        int c2 = line.indexOf(',', c1 + 1);
        int c3 = line.indexOf(',', c2 + 1);
        if (c1 < 0 || c2 < 0 || c3 < 0) return false;

        shoulder.set_angle(line.substring(0, c1).toInt());
        elbow.set_angle(line.substring(c1 + 1, c2).toInt());
        wrist.set_angle(line.substring(c2 + 1, c3).toInt());
        claw.set_angle(line.substring(c3 + 1).toInt());
        Serial.println("received");
        return true;
    }
};

//Functions
ARM arm(2,3,4,5);

void setup() {
  Serial.begin(115200);
  arm.begin();
  }

void loop(){
  arm.receive();
}