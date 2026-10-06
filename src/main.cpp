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
char rx_byte;

// Variable definitions
const short ANGLE_TOLERANCE = 10;
int Target_angle;
short int motor_index;

float receive(){
    String line = Serial.readStringUntil('\n');
    int comma = line.indexOf(',');
    int index = line.substring(0, comma).toInt();
    float angle = line.substring(comma + 1).toFloat();   
    return index, angle;
}

int Comparison(int current, int target) {
  if (current < target - ANGLE_TOLERANCE){ 
    return current ++;
  }
  else if (current > target + ANGLE_TOLERANCE){
     return current --;
  }
}


void control(int index,float Target_angle){
  switch (index){
    case 0:
      //Shoulder Motor
      shoulder_angle = Comparison(shoulder_angle,Target_angle);
      shoulder_servo.write(shoulder_angle);  
      break;
    case 1:
      //elbow Motor
      elbow_angle = Comparison(elbow_angle,Target_angle);
      elbow_servo.write(elbow_angle);
      break;
    case 2:
      //Wrist Motor
      wrist_angle = Comparison(wrist_angle,Target_angle);
      wrist_servo.write(wrist_angle);
      break;
    case 3:
      // Claw Motor
      printf("test");
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
  if (Serial.available() < 1){
    printf("no data");
  }
  else if(Serial.available() > 0){
    motor_index, Target_angle = receive();    
    control(motor_index, Target_angle);
  }

}
