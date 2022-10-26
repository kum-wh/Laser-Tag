#include <Wire.h>
#include "CRC.h"
#include "CRC8.h"

#define FEEDBACK A3

CRC8 crc;

bool handshakeFlag = false;
bool handshakeStart = false;

unsigned long currentTime = 0;
unsigned long previousBeetle1Time = 0;
unsigned long handshakeStartTime = 0;
unsigned long handshakeEndTime = 0;
int samplingPeriod = 10; // 100 Hz
int sampleCount = 20;

int isCalibrated = 0;

byte beetle1Buffer[12];

float accX, accY, accZ; // accelerometer data read from IMU
float gyroX, gyroY, gyroZ; // gyroscope data read from IMU
float temperature; // temperature will be read but ignored

// from calibration
float accXOffset = 0.0, accYOffset = 0.0, accZOffset = 0.0;
float gyroXOffset = 0.0, gyroYOffset = 0.0, gyroZOffset = 0.0;

float accScaleFactor = 8192.0;
float gyroScaleFactor = 65.5;
float gForce = 9.80665;

float avgAccX = 0.0, avgAccY = 0.0, avgAccZ = 0.0;
float avgGyroX = 0.0, avgGyroY = 0.0, avgGyroZ = 0.0;

int16_t finalAccX, finalAccY, finalAccZ;
int16_t finalGyroX, finalGyroY, finalGyroZ;

int16_t prevFinalAccX, prevFinalAccY, prevFinalAccZ;
int16_t prevFinalGyroX, prevFinalGyroY, prevFinalGyroZ;

int16_t deltaAccX, deltaAccY, deltaAccZ;
int16_t deltaGyroX, deltaGyroY, deltaGyroZ;

bool startOfMove = false;
int burst = 0;
int burstCount = 50;

void(* resetFunc) (void) = 0;

void initRegisters() {
  
  // Start up the IMU and do a reset
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  // Configure the accelerometer and set range to +-4g
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x08);
  Wire.endTransmission();

  // Configure the gyroscope and set range to +-500 deg/s
  Wire.beginTransmission(0x68);
  Wire.write(0x1B);
  Wire.write(0x08);
  Wire.endTransmission();
}

void calibrateDLPF() {

  // point to CONFIG register
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.endTransmission();

  // read original value, clear DLPF setting, and set new DLPF setting
  Wire.requestFrom(0x68, 1);
  byte reg = Wire.read();
  reg &= 0xF8;
  reg |= 0x06;

  // write new value to CONFIG
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.write(reg);
  Wire.endTransmission();
}

void calibrateSensor() {
  flashLedForThreeSeconds(); // prepare the player for calibration
  
  for (int count = 0; count < 1000; count++) {
    
//    if (count % 200 == 0) {
//      Serial.print(".");
//    }
    
    readRegisters();

    accXOffset += accX;
    accYOffset += accY;
    accZOffset += accZ;
    
    gyroXOffset += gyroX;
    gyroYOffset += gyroY;
    gyroZOffset += gyroZ;

    delay(3);
  }

  accXOffset /= 1000;
  accYOffset /= 1000;
  accZOffset /= 1000;
  
  gyroXOffset /= 1000;
  gyroYOffset /= 1000;
  gyroZOffset /= 1000;

  onLed();

//  Serial.println(" done");
}

void readRegisters() {
  Wire.beginTransmission(0x68);
  Wire.write(0x3B); // Start by pointing to MSB of ACCEL_XOUT register
  Wire.endTransmission();

  Wire.requestFrom(0x68, 14); // Request 14 bytes from the slave

  // read and convert to appropriate units
  // acceleration is in m/s^2
  // gyroscope is in deg per sec
  accX = ((Wire.read() << 8 | Wire.read()) / accScaleFactor) * gForce;
  accY = ((Wire.read() << 8 | Wire.read()) / accScaleFactor) * gForce;
  accZ = ((Wire.read() << 8 | Wire.read()) / accScaleFactor) * gForce;
  temperature = Wire.read() << 8 | Wire.read(); // read but ignored
  gyroX = (Wire.read() << 8 | Wire.read()) / gyroScaleFactor;
  gyroY = (Wire.read() << 8 | Wire.read()) / gyroScaleFactor;
  gyroZ = (Wire.read() << 8 | Wire.read()) / gyroScaleFactor;
}

void setup() {
  Wire.begin();
  Serial.begin(115200);

  handshakeFlag = false;
  handshakeStart = false;
  currentTime = 0;
  previousBeetle1Time = 0;
  handshakeStartTime = 0;
  handshakeEndTime = 0;

  pinMode(FEEDBACK, OUTPUT); 

  // for individual testing
//  handshakeFlag = tru0e;
//  initRegisters();
//  calibrateDLPF();
//  calibrateSensor();
}

void readBeetle1() {
  for (int i = 0; i < sampleCount; i++) {
    readRegisters();
  
    accX -= accXOffset;
    accY -= accYOffset;
    accZ -= accZOffset;
  
    gyroX -= gyroXOffset;
    gyroY -= gyroYOffset;
    gyroZ -= gyroZOffset;

    avgAccX += accX;
    avgAccY += accY;
    avgAccZ += accZ;

    avgGyroX += gyroX;
    avgGyroY += gyroY;
    avgGyroZ += gyroZ;
  }

  avgAccX /= sampleCount;
  avgAccY /= sampleCount;
  avgAccZ /= sampleCount;

  avgGyroX /= sampleCount;
  avgGyroY /= sampleCount;
  avgGyroZ /= sampleCount;

  prevFinalAccX = finalAccX;
  prevFinalAccY = finalAccY;
  prevFinalAccZ = finalAccZ;
  prevFinalGyroX = finalGyroX;
  prevFinalGyroY = finalGyroY;
  prevFinalGyroZ = finalGyroZ;

  finalAccX = (int16_t)(avgAccX * 100);
  finalAccY = (int16_t)(avgAccY * 100);
  finalAccZ = (int16_t)(avgAccZ * 100);
  finalGyroX = (int16_t)(avgGyroX);
  finalGyroY = (int16_t)(avgGyroY);
  finalGyroZ = (int16_t)(avgGyroZ);

  deltaAccX = abs(finalAccX - prevFinalAccX);
  deltaAccY = abs(finalAccY - prevFinalAccY);
  deltaAccZ = abs(finalAccZ - prevFinalAccZ);
  deltaGyroX = abs(finalGyroX - prevFinalGyroX);
  deltaGyroY = abs(finalGyroY - prevFinalGyroY);
  deltaGyroZ = abs(finalGyroZ - prevFinalGyroZ);

  if (deltaAccX > 300 || deltaAccY > 300 || deltaAccZ > 300) {
    startOfMove = true;
  }

  // average values
//  Serial.print(avgAccX); Serial.print(" ");
//  Serial.print(avgAccY); Serial.print(" ");
//  Serial.print(avgAccZ); Serial.print(" ");
//  Serial.print(avgGyroX); Serial.print(" ");
//  Serial.print(avgGyroY); Serial.print(" ");
//  Serial.print(avgGyroZ); Serial.print(" ");

  // raw values
//  Serial.print(accX); Serial.print(" ");
//  Serial.print(accY); Serial.print(" ");
//  Serial.print(accZ); Serial.print(" ");
//  Serial.print(gyroX); Serial.print(" ");
//  Serial.print(gyroY); Serial.print(" ");
//  Serial.print(gyroZ); Serial.print(" ");

  // final values
//  Serial.print(finalAccX); Serial.print(" ");
//  Serial.print(finalAccY); Serial.print(" ");
//  Serial.print(finalAccZ); Serial.print(" ");
//  Serial.print(finalGyroX); Serial.print(" ");
//  Serial.print(finalGyroY); Serial.print(" ");
//  Serial.print(finalGyroZ); Serial.print(" ");
//
//  Serial.println("");

  // reset the values
  avgAccX = 0.0;
  avgAccY = 0.0;
  avgAccZ = 0.0;

  avgGyroX = 0.0;
  avgGyroY = 0.0;
  avgGyroZ = 0.0;
}

void printData() {
  // 0 - logout
  // 1 - shield
  // 2 - grenade
  // 3 - reload
  // 4 - idle
  Serial.print("3,");
  
  Serial.print(finalAccX); Serial.print(",");
  Serial.print(finalAccY); Serial.print(",");
  Serial.print(finalAccZ); Serial.print(",");
  Serial.print(finalGyroX); Serial.print(",");
  Serial.print(finalGyroY); Serial.print(",");
  Serial.print(finalGyroZ);

  Serial.println("");
}

void loop() {

//  while (millis() - previousBeetle1Time < samplingPeriod);
//  previousBeetle1Time = millis();
//  readBeetle1();
//  if (startOfMove) {
//    while (burst < burstCount && millis() - previousBeetle1Time > samplingPeriod) {
//      previousBeetle1Time = millis();
//      readBeetle1();
//      printData();
//      burst++;
//    }
//    startOfMove = false;
//    burst = 0;
//  }
//  delay(300);
  
  if (Serial.available()) {
    byte packetType = Serial.read();
  
    switch (packetType) {
        case 'H':
            handshakeStart = true;
            handshakeFlag = false;
            Serial.write('A');
            crc.add('A');
            Serial.write(crc.getCRC());
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.flush();
            handshakeStartTime = millis();
            crc.restart();
            break;
        case 'A':
            // Received last ACK from laptop. Handshake complete
            handshakeFlag = true;
            handshakeStart = false;
            initRegisters();
            calibrateDLPF();
            calibrateSensor();
            break;
        case 'R':
            handshakeFlag = false;
            handshakeStart = false;
            resetFunc();
            break;
    }
  }
  if (handshakeStart == true && handshakeFlag == false) {
            handshakeEndTime = millis();
            if (handshakeEndTime - handshakeStartTime > 1000) {
            Serial.write('A');
            crc.add('A');
            Serial.write(crc.getCRC());
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.write(0);
            Serial.flush();
            crc.restart();
            handshakeStartTime = handshakeEndTime;
            }
  }
  
  if (handshakeFlag) {
    currentTime = millis();
    if (currentTime - previousBeetle1Time > samplingPeriod) {
      readBeetle1();
      if (startOfMove) {
        while (burst < burstCount && millis() - previousBeetle1Time > samplingPeriod) {
          previousBeetle1Time = millis();
          readBeetle1();
          Serial.write('D');
          crc.add('D');
          beetle1Buffer[0] = (finalAccX >> 8) & 255;
          beetle1Buffer[1] = (finalAccX) & 255;
          beetle1Buffer[2] = (finalAccY >> 8) & 255;
          beetle1Buffer[3] = (finalAccY) & 255;
          beetle1Buffer[4] = (finalAccZ >> 8) & 255;
          beetle1Buffer[5] = (finalAccZ) & 255;
          beetle1Buffer[6] = (finalGyroX >> 8) & 255;
          beetle1Buffer[7] = (finalGyroX) & 255;
          beetle1Buffer[8] = (finalGyroY >> 8) & 255;
          beetle1Buffer[9] = (finalGyroY) & 255;
          beetle1Buffer[10] = (finalGyroZ >> 8) & 255;
          beetle1Buffer[11] = (finalGyroZ) & 255;
          Serial.write(beetle1Buffer, 12);
          crc.add(beetle1Buffer, 12);
          Serial.write(crc.getCRC());
          crc.restart();
          Serial.write(0);
          Serial.write(0);
          Serial.write(0);
          Serial.write(0);
          Serial.write(0);
          Serial.write(0);
          Serial.flush();

          burst++;
        }
        startOfMove = false;
        burst = 0;
      }
    }
  }
}

void flashLedForThreeSeconds() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(FEEDBACK, HIGH);
    delay(250);
    digitalWrite(FEEDBACK, LOW);
    delay(250);
  }
}

void onLed() {
  digitalWrite(FEEDBACK, HIGH);
}
