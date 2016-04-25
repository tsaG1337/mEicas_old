
#include <Wire.h> //Include I2C Library
//#define DEBUG
//********** Defining Debug Mode **********//
#ifdef DEBUG
#define DEBUG_PRINT(x) Serial.println(x)
#else
#define DEBUG_PRINT(x)
#endif

//********** Setup **********//

#define SOFTVERSION 001  //Software Version
#define HARDVERSION 162  //Hardware Version
#define ID "00000003"            //Serial Number
#define NAME "AnalogCore" // Device Name

#define AnalogReadSampleRate 5 //Oversampling rate for analog readings
#define AnalogOffset 0 //Analog Offset hast to be calibrated for each chip
#define I2CAdress 0x22 // I2C Adress

//********** Defining Pins **********//
#define P1LED 13 //Green Status LED P1
#define P2LED 41 //Red Status LED P2
#define MCTNLED 65 // Master Caution LED
#define StatusLED 32 //Status LED
#define PowerInVoltagePin A10 //Power Sensing Pin for Voltage Input
#define BatteryInVoltagePin DAC1  //Battery Input Voltage ##CONNECTED TO DAC

uint8_t NTCPin[8] = {A9, A5, A8, A4, A7, A3, A6, A2};
uint8_t TachoPin[2] = { 36, 94};


#define BatteryEnablePin 2 //Pin to enable the Battery Boost converter
#define BatteryChargePin 6 //Pin to enable the Battery charger
#define BatteryStat1Pin 0 //Charger Status Pin1 ##SET CORRECT PIN
#define BatteryStat2Pin 0//Charger Status Pin2 ##SET CORRECT PIN  
#define BatteryProgPin 0 //                     
char buttonPin[8] = {48, 49, 50, 51, 44, 45, 46, 47};

//********** Defining Status Variables **********//
String rxString = "";
int NTCValue[8] = {0, 0, 0, 0, 0, 0, 0, 0};
uint16_t Tacho1 = 0;
uint16_t Tacho2 = 0;
int timer1 = 0;
int timer2 = 0;
char requestedData = 0;
uint16_t PowerInVoltage = 0;

uint8_t BatteryChargeStat = 0;
uint16_t BatteryInVoltage = 0;  //TO BE TESTED
uint8_t BatteryEnabled = 0;
uint8_t MCTN = 0;
uint16_t MCTNtime = 0;
uint16_t MCTNtimeOld = 0;
uint8_t MCTNintervall = 500;
uint8_t MCTNstate = 0;

//********** Defining Button Variables **********//
const long interval = 500;    // Updating Sensors intervall (milliseconds)
uint8_t requestedbyte = 0; //I2C request Byte
bool buttonState[8];             // the current reading[i] from the input pin
bool lastbuttonState[8] = {0, 0, 0, 0, 0, 0, 0, 0}; // the previous reading[i] from the input pin
long lastDebounceTime[8] = {0, 0, 0, 0, 0, 0, 0, 0}; // the last time the output pin was toggled
long debounceDelay = 50; // Debounce Delay

void setup() {

  //REG_ADC_MR = (REG_ADC_MR & 0xFFF0FFFF) | 0x00020000; //Speed up the ADC Reading
  Serial1.begin(9600); //Serial Port for the RS232 Interface
  Serial.begin(9600);
  analogReadResolution(12); // set ADC resolution to 12 bit
  Wire.begin(I2CAdress); //joining I2C Bus as Master
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  //**** Defining LED Variables ****//
  pinMode(P1LED, OUTPUT);
  pinMode(P2LED, OUTPUT);
  digitalWrite(P1LED, LOW);
  digitalWrite(P2LED, LOW);
  pinMode(StatusLED, OUTPUT);
  pinMode(MCTNLED, OUTPUT);
  digitalWrite(MCTNLED, LOW);

  //**** Declare NTC Pins as Interrupts ****//
  for (int i = 0; i < 8; i++) {
    pinMode(NTCPin[i], INPUT);
  }

  //**** Declare Tacho Pins as  ****//
  for (int i = 0; i < 2; i++) {
    pinMode(TachoPin[i], INPUT);
  }

  pinMode(BatteryEnablePin, OUTPUT); //Pin to enable the Battery Boost converter
  //pinMode(BatteryStat1Pin, INPUT);
  //pinMode(BatteryStat2Pin, INPUT);
  //pinMode(BatteryProgPin, INPUT);

  //attach Interrupts
  attachInterrupt(TachoPin[0], readTacho1, RISING); //Intterupt for Tacho1
  attachInterrupt(TachoPin[1], readTacho2, RISING); //Intterupt for Tacho2

  //for (int i = 0; i < 8; i++) {
  //  pinMode(buttonPin[i], INPUT);
  //}

}
void loop() {
  checkMCTN();
  //if (Serial.available())  {
  //    char c = Serial.read();  //gets one byte from serial buffer
  //    if (c == '\r') {  //looks for end of data packet marker
  //      Serial.read(); //gets rid of following \n
  //      //do something with rx string
  //
  //      rxString=""; //clear variable for new input
  //     }
  //    else {
  //      rxString += c; //add the char to rxString
  //    }
  //  }
}

//********** Power Input Voltage Reading (mV) **********//
uint16_t getPowerInputVoltage() {
  uint32_t values;
  for (int i = 0; i < AnalogReadSampleRate; i++) {
    //delay(1);
    values += (analogRead(PowerInVoltagePin));
  }
  uint16_t sensorValue = (values / AnalogReadSampleRate) + AnalogOffset; //Digital Voltage
  uint32_t U = 3300 * sensorValue / 4096; //Voltage on Chip Pin
  PowerInVoltage = (9070 * U / 1000) + U; //External Voltage calculated through Voltage divider

  return PowerInVoltage;
}

//********** Temperature Reading **********//
uint8_t readNTC(uint8_t NTCPin) {
  int values = 0;
  for (int i = 0; i < AnalogReadSampleRate; i++) {
    values += (analogRead(NTCPin));
  }
  uint16_t sensorValue = (values / AnalogReadSampleRate) + AnalogOffset; //Digital Voltage
  uint16_t U = 3300 * sensorValue / 4096; //Voltage on Chip Pin
  
  uint16_t R;
  R = (4650 * (U / 2)) / (3300 - (U / 2));
  float logCalc = R / 5000.0000;
  uint32_t T = (3984 * 298) / (3984 + log(logCalc) * 298);
  return T - 273;
}

//********** Tacho Reading **********//
void readTacho1() {
  int currenttime = micros();
  int microtime = currenttime - timer1;
  Tacho1 = 60000000 / microtime;
  timer1 = currenttime;
}
void readTacho2() {
  int currenttime = micros();
  int microtime = currenttime - timer2;
  Tacho2 = 60000000 / microtime;
  timer2 = currenttime;
}


//********** Button Read & Debounce **********//
void readButtons() {
  bool reading[8] = {0, 0, 0, 0, 0, 0, 0, 0};
  for (int i = 0; i <= 7; i++) {
    reading[i] = digitalRead(buttonPin[i]);

    // check to see if you just pressed the button
    // (i.e. the input went from LOW to HIGH),  and you've waited
    // long enough since the last press to ignore any noise:

    // If the switch changed, due to noise or pressing:
    if (reading[i] != lastbuttonState[i]) {
      // reset the debouncing timer
      lastDebounceTime[i] = millis();
    }

    if ((millis() - lastDebounceTime[i]) > debounceDelay) {
      // whatever the reading[i] is at, it's been there for longer
      // than the debounce delay, so take it as the actual current state:
      if (reading[i] != buttonState[i]) {// if the button state has changed:
        buttonState[i] = reading[i];
      }
    }
    // save the reading[i].  Next time through the loop,
    // it'll be the lastbuttonState[i]:
    lastbuttonState[i] = reading[i];
  }
}

//****** Backup Battery Supply *******//

//enable backup Battery

void setBackupBattery(bool state) {
  digitalWrite(BatteryEnablePin, state);
}

//read battery voltage  (mV)
uint8_t readBatteryInputVoltage() {
  uint32_t values;
  for (int i = 0; i < AnalogReadSampleRate; i++) {
    values += (analogRead(BatteryInVoltagePin));
  }
  int sensorValue = values / AnalogReadSampleRate;
  BatteryInVoltage = ((sensorValue * 330) / 4095) * 10 - AnalogOffset;
  return BatteryInVoltage;
}

//enable Battery charging
void setBatteryCharge(bool state) {
  digitalWrite(BatteryChargePin, state);
}
bool getBatteryCharge() {
  return digitalRead(BatteryChargePin);
}

/*read Battery charging Status

  +=======================+=======+=======+======+
  |  Charge Cycle State   | Stat1 | Stat2 |  PG  |
  +=======================+=======+=======+======+
  | Shutdown              | High  | High  | High |
  +-----------------------+-------+-------+------+
  | Standby               | High  | High  | Low  |
  +-----------------------+-------+-------+------+
  | Charge in Progress    | Low   | High  | Low  |
  +-----------------------+-------+-------+------+
  | Charge Complete (EOC) | High  | Low   | Low  |
  +-----------------------+-------+-------+------+
  | Temperature Fault     | High  | High  | Low  |
  +-----------------------+-------+-------+------+
  | Timer Fault           | High  | High  | Low  |
  +-----------------------+-------+-------+------+
  | System Test Mode      | Low   | Low   | Low  |
  +-----------------------+-------+-------+------+
*/
uint8_t getBatteryChargeStat() {
  bool  statusArray[2];
  statusArray[0] = digitalRead(BatteryStat1Pin);  //read each Pin into the array
  statusArray[1] = digitalRead(BatteryStat1Pin);
  statusArray[2] = digitalRead(BatteryProgPin);
  for (int i = 0; i < 8; i++)
  {
    bitWrite(BatteryChargeStat, 7 - i, statusArray[i]); //convert Bitarray to integer
  }

  return BatteryChargeStat;
}

//********** I2C functions **********//
void requestEvent()
{
  switch (requestedbyte) {
    case 1: { //Sends the Device Name
        String DeviceName = NAME;
        uint8_t buf [DeviceName.length() + 1]; //Create Buffer with length +1
        DeviceName.getBytes(buf, DeviceName.length() + 1); //Convert String to Char Array
        for (int i = 0; i < sizeof buf; i++) {
          Wire.write(buf[i]);
        }
        break;
      }
    case 2: { //Sends the Device Hardware ID (Serial)
        Wire.write(ID);
        break;
      }
    case 3: { //Sends the Device Hardware Version
        Wire.write(HARDVERSION);
        break;
      }
    case 4: { //Sends the Device Software Version
        Wire.write(SOFTVERSION);
        break;
      }
    case 5: { // Sends the Device PowerInput Voltage
        I2cBigWrite(getPowerInputVoltage());
        break;
      }
    case 6: { // Sends the Temperature values
        Wire.write(NTCValue[0]);
        break;
      }
    case 7: { // Sends the Temperature values
        Wire.write(NTCValue[1]);
        break;
      }
    case 8: { // Sends the Temperature values
        Wire.write(NTCValue[2]);
        break;
      }
    case 9: { // Sends the Temperature values
        Wire.write(NTCValue[3]);
        break;
      }
    case 10: { // Sends the Temperature values
        Wire.write(NTCValue[4]);
        break;
      }
    case 11: { // Sends the Temperature values
        Wire.write(NTCValue[5]);
        break;
      }
    case 12: { // Sends the Temperature values
        Wire.write(NTCValue[6]);
        break;
      }
    case 13: { // Sends the Temperature values
        Wire.write(NTCValue[7]);
        break;
      }
    case 14: { // Sends the Tacho values
        I2cBigWrite(Tacho1);
        break;
      }
    case 15: { // Sends the Tacho values
        I2cBigWrite(Tacho2);
        break;
      }
    case 16: { //send the BatteryCharging Status
        Wire.write(BatteryChargeStat);
      }
    case 17: { //Battery Status Bit
        Wire.write(BatteryEnabled);
      }
  }
}

void receiveEvent(int howMany) {
  bool state = 0;
  while (Wire.available())
  {
    // read I2C value
    requestedbyte = Wire.read();

    // toggle LED to indicate I2C traffic
    if (state == 0)
    {
      digitalWrite(P2LED, HIGH); // turn the LED on
      state = 1;
    }
    else
    {
      digitalWrite(P2LED, LOW); // turn the LED off
      state = 0;
    }
  }

  digitalWrite(P1LED, LOW); // set the LED off
  DEBUG_PRINT("Received request with following Adress pointer: " + requestedbyte);
}

void I2cBigWrite(int bigVal) {
  digitalWrite(P2LED, HIGH); // set the LED on
  Wire.write((byte *)&bigVal, sizeof(int));
  digitalWrite(P2LED, LOW); // set the LED on

}

//********** NMEA Functions **********//
void processString(String data) {
  String commandType = "";

  commandType = chopString(data, ',', 0);

  const int arraySize = 6; // look for our value in our dictionary
  String ary[arraySize] = {"", "", "", "", "", ""}; //NMEA dictionary
  int arrayPos;
  for (int i = 0; i < arraySize; i++) {
    if (commandType = ary[i]) {
      arrayPos = i;
      break;
    }
    switch (arrayPos) {
      case 1: {
          //Sends the Device Name
        }
        break;
    }

  }
}
String chopString(String data, char separator, int index) {

  int maxIndex = data.length() - 1;
  int j = 0;
  String chunkVal = "";

  for (int i = 0; i <= maxIndex && j <= index; i++)
  {
    chunkVal.concat(data[i]);

    if (data[i] == separator)
    {
      j++;

      if (j > index)
      {
        chunkVal.trim();
        return chunkVal;
      }

      chunkVal = "";
    }
  }
}
void checkMCTN() {
  if (MCTN) {
    uint16_t currentMillis = millis();
    if (currentMillis - MCTNtimeOld >= MCTNintervall) {
      // save the last time the LED blinked
      MCTNtimeOld = currentMillis;

      // if the LED is off turn it on and vice-versa:
      MCTNstate != MCTNstate;
      digitalWrite(MCTNLED, MCTNstate);
    }
  }
}

