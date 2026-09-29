
#include <Arduino.h>
#include <Servo.h>
// put function declarations here:
int myFunction(int, int);
Servo shoulder_servo;
Servo elbow_servo;
Servo wrist_servo;
const short shoulder_servo_pin=2;
const short elbow_servo_pin=3;
const short wrist_servo_pin=4;
int shoulder_angle = 0;
int elbow_angle = 0;
int wrist_angle = 0;
void setup() {
  Serial.begin(9600);
  shoulder_servo.attach(shoulder_servo_pin);
  elbow_servo.attach(elbow_servo_pin);
  wrist_servo.attach(wrist_servo_pin);
  }

void loop() {
  digitalWrite(11,LOW);
  if(Serial.available() > 0){
    String msg = Serial.readStringUntil('\n');
    msg.trim();
    if (msg == "q"){
      shoulder_angle ++;
      shoulder_servo.write(shoulder_angle);
    }
    else if(msg == "w"){
      shoulder_angle --;
      shoulder_servo.write(shoulder_angle);
    }
    else if(msg == "a"){
      elbow_angle ++;
      elbow_servo.write(elbow_angle);

    }
    else if(msg =="s"){
      elbow_angle --;
      elbow_servo.write(elbow_angle);
    }
    else if(msg == "z"){
      wrist_angle ++;
      wrist_servo.write(wrist_angle);
    }
    else if(msg =="x"){
      wrist_angle --;
      wrist_servo.write(wrist_angle);
        digitalWrite(wrist_servo_pin,LOW);
      //turn wrist CCW
    }
    else {
      printf("No viable commands");
  }
    
}
else{

}

  // digitalWrite(shoulder_servo_pin,HIGH);
  // digitalWrite(elbow_servo_pin,HIGH);
  // digitalWrite(wrist_servo_pin,HIGH);
  // delay(1000);
}
// put function definitions here:
