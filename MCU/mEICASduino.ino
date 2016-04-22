#include <Button.h>
#include <Encoder.h>
#include <Wire.h>
#define Stepsperclick 4
// Change these two numbers to the pins connected to your encoder.
//   Best Performance: both pins have interrupt capability
//   Good Performance: only the first pin has interrupt capability
//   Low Performance:  neither pin has interrupt capability
Encoder myEnc(6, 5);
Button button = Button(7, BUTTON_PULLUP_INTERNAL, true, 100);
Button left = Button(2, BUTTON_PULLUP, true, 100);
Button middle = Button(3, BUTTON_PULLUP, true, 100);
Button right = Button(4, BUTTON_PULLUP, true, 100);
//   avoid using pins with LEDs attached

void setup() {
  Serial.begin(9600);
  Serial.println("Basic Encoder Test:");
    pinMode(13, OUTPUT);
    //I2C Config
Wire.begin(0x66);                // join i2c bus with address #2
Wire.onRequest(requestEvent); // register event
    
}

long oldPosition  = -128;
char cursorpos = 0;
void loop() {
  long newPosition = (myEnc.read()/Stepsperclick);
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    Serial.println(newPosition);
    myEnc.write(0);
    oldPosition=0;
  }
   if(button.uniquePress()){
    Serial.println("Rotary Pressed");
    cursorpos = 4;
  }
  if(right.uniquePress()){
    Serial.println("right Pressed");
    cursorpos = 3;
  }
  if(left.uniquePress()){
    Serial.println("left Pressed");
    cursorpos = 1;
  }
  if(middle.uniquePress()){
    Serial.println("middle Pressed");
    cursorpos = 2;
  }
}
void requestEvent()
{
  Wire.write(cursorpos);
  cursorpos = 0;
  
}
