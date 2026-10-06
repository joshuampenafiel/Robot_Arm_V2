#include <Arduino.h>
#include <Servo.h>

//Servo definitions
Servo shoulder_servo;
Servo elbow_servo;
Servo wrist_servo;

const short shoulder_servo_pin=2;
const short elbow_servo_pin=3;
const short wrist_servo_pin=4;

int shoulder_angle = 0;
int elbow_angle = 0;
int wrist_angle = 0;
const int number_of_motors = 3;
//Serial definitions

const size_t PAYLOAD_SIZE = 2 * sizeof(float);
const char START_MARKER = 0x02;
const char END_MARKER = 0x03;
const float msg[2];
char rx_byte;

// Variable definitions
const short ANGLE_TOLERANCE = 10;
int Target_angle;
short int motor_index;

bool receive(int &index, float &angle) {
  String line = Serial.readStringUntil('\n');
  int comma = line.indexOf(',');
  if (comma < 0) return false;
  index = line.substring(0, comma).toInt();
  angle = line.substring(comma + 1).toFloat();
  return true;
}

int comparison(int current, int target) {
  if (current < target - ANGLE_TOLERANCE){ 
    return current + 1;
  }
  else if (current > target + ANGLE_TOLERANCE){
     return current - 1;
  }
  else{
    return current;
  }
}


void control(int index,float Target_angle){
  switch (index){
    case 0:
      //Shoulder Motor
      shoulder_angle = comparison(shoulder_angle,Target_angle);
      shoulder_servo.write(shoulder_angle);  
      break;
    case 1:
      //elbow Motor
      elbow_angle = comparison(elbow_angle,Target_angle);
      elbow_servo.write(elbow_angle);
      break;
    case 2:
      //Wrist Motor
      wrist_angle = comparison(wrist_angle,Target_angle);
      wrist_servo.write(wrist_angle);
      break;
    case 3:
      // Claw Motor

      break;
    
    default:
      break;
  }
}


void setup() {  
  Serial.begin(9600);
  shoulder_servo.attach(shoulder_servo_pin);
  elbow_servo.attach(elbow_servo_pin);
  wrist_servo.attach(wrist_servo_pin);
  }

void loop() {
  for(int i =0; i < number_of_motors; i++){
    bool ok;
    if (Serial.available() > 0) {
      int index;
      float angle;
      ok = receive(index, angle);
      if (ok){
       control(index, angle);
      }
      else{
        break;
      }
  }

    Serial.println(ok ? "complete" : "bad");
  }

}
