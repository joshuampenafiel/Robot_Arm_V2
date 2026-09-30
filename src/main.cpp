#include <Arduino.h>
#include <Servo.h>
#include <vector>

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

std::vector<float> receive(){
  if (Serial.read() == START_MARKER){
    uint8_t buffer[PAYLOAD_SIZE];
    size_t bytesRead = Serial.readBytes((char*)buffer, PAYLOAD_SIZE);
    if (bytesRead == PAYLOAD_SIZE && Serial.read() == END_MARKER){
      memcpy(msg,buffer,PAYLOAD_SIZE);
      Serial.print("Received successfully. First element: ");
      Serial.println(msg[0]);
      }
    }
    return msg;

}

void Offset(current, target){
  if (current < target - ANGLE_TOLERANCE) return current ++;
  if (current > target + ANGLE_TOLERANCE) return current --;

void setup() {  
  Serial.begin(9600);
  shoulder_servo.attach(shoulder_servo_pin);
  elbow_servo.attach(elbow_servo_pin);
  wrist_servo.attach(wrist_servo_pin);
  }

void loop() {
  if(Serial.available() > 0){

    angle = receive() 
    
    if (angle[0] == 0_


    if (msg[1] == ){
      shoulder_angle ++;
      shoulder_servo.write(shoulder_angle);
    }
    else if(msg[1] == "w"){
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
