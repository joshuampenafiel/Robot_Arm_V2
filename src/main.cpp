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

//Serial definitions

const int VECTOR_SIZE = 2;
const size_t PAYLOAD_SIZE = VECTOR_SIZE * sizeof(float);
const char START_MARKER = 0x02;
const char END_MARKER = 0x03;
const float msg[VECTOR_SIZE];


// Variable definitions
const short ANGLE_TOLERANCE = 10;

float receive(){
  if (Serial.read() != START_MARKER){
    return NAN;
  }
    
  uint8_t buffer[PAYLOAD_SIZE];
  size_t bytesRead = Serial.readBytes(buffer, PAYLOAD_SIZE);

  if (bytesRead != PAYLOAD_SIZE || Serial.read() != END_MARKER){
      return NAN;
      }
  
  float msg;
  memcpy(&msg, buffer, sizeof(msg));
  return msg;
}

int Offset(int current, int target) {
  if (current < target - ANGLE_TOLERANCE){ 
    return current ++;
  }
  if (current > target + ANGLE_TOLERANCE){
     return current --;
  }
}

void setup() {  
  Serial.begin(9600);
  shoulder_servo.attach(shoulder_servo_pin);
  elbow_servo.attach(elbow_servo_pin);
  wrist_servo.attach(wrist_servo_pin);
  }

void loop() {
  if (Serial.available() < 1){
    printf("no data");
  }
  else if(Serial.available() > 0){

    int Target_angle = receive();

    int Current_angle = 1;
    int change = Offset(Current_angle,Target_angle);
    
    shoulder_servo.write(shoulder_angle);

    elbow_servo.write(elbow_angle);

    wrist_servo.write(wrist_angle);
    printf("Test");
  }

}
