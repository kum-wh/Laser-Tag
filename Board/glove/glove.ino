// Adapted from https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/ 
// and https://github.com/TKJElectronics/KalmanFilter/blob/master/examples/MPU6050/I2C.ino 

#include <Wire.h>
#include <Ewma.h>

const uint8_t IMU_ADDR = 0x68; // AD0 is logic low on the PCB
const uint8_t ACC_REG = 0x3B;
const uint8_t GYRO_REG = 0x43;

const uint16_t I2C_TIMEOUT = 1000; // Used to check for errors in I2C communication

const float ACC_SCALE = 125 / 16384.0;
const float GYRO_SCALE = 1 / 131.0;

uint32_t timer;
uint8_t i2cData[14]; // Buffer for I2C data

int16_t accX, accY, accZ;
int16_t gyroX, gyroY, gyroZ;

int16_t accXErr = 0, accYErr = 0, accZErr = 0;
int16_t gyroXErr = 0, gyroYErr = 0, gyroZErr = 0;

// Less smoothing - faster to detect changes, but more prone to noise
Ewma accXFilter(0.2), accYFilter(0.2), accZFilter(0.2);
// More smoothing - less prone to noise, but slower to detect changes
Ewma gyroXFilter(0.05), gyroYFilter(0.05), gyroZFilter(0.05);

int16_t accXFiltered, accYFiltered, accZFiltered;
int16_t gyroXFiltered, gyroYFiltered, gyroZFiltered;

const int16_t accThreshold = 75;
const int16_t gyroThreshold = 80;
int numSent = -1;
const int numToSend = 350;

void setup() {
  Serial.begin(115200);

  i2cData[0] = 7; // Set the sample rate to 1000Hz, since accelerometer output rate is 1000Hz
  i2cData[1] = 0x00; // Disable FSYNC and set 260 Hz Acc filtering (LPF), 256 Hz Gyro filtering (LPF), 8 KHz sampling
  i2cData[2] = 0x00; // Set Gyro Full Scale Range to ±250deg/s
  i2cData[3] = 0x00; // Set Accelerometer Full Scale Range to ±2g
  while (i2cWrite(0x19, i2cData, 4, false)); // Write to all four registers at once
  while (i2cWrite(0x6B, 0, true)); // disable sleep mode
  
  delay(100); // Wait for sensor to stabilize
  calculateErrors();
}

void loop() {
  while (i2cRead(ACC_REG, i2cData, 6));
  accX = (int16_t)((i2cData[0] << 8) | i2cData[1]) * ACC_SCALE - accXErr;
  accY = (int16_t)((i2cData[2] << 8) | i2cData[3]) * ACC_SCALE - accYErr;
  accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]) * ACC_SCALE - accZErr;

  accXFiltered = accXFilter.filter(accX);
  accYFiltered = accYFilter.filter(accY);
  accZFiltered = accZFilter.filter(accZ);

  while (i2cRead(GYRO_REG, i2cData, 6));
  gyroX = (int16_t)((i2cData[0] << 8) | i2cData[1]) * GYRO_SCALE - gyroXErr;
  gyroY = (int16_t)((i2cData[2] << 8) | i2cData[3]) * GYRO_SCALE - gyroYErr;
  gyroZ = (int16_t)((i2cData[4] << 8) | i2cData[5]) * GYRO_SCALE - gyroZErr;

  gyroXFiltered = gyroXFilter.filter(gyroX);
  gyroYFiltered = gyroYFilter.filter(gyroY);
  gyroZFiltered = gyroZFilter.filter(gyroZ);

  if (accXFiltered > accThreshold || accXFiltered < -accThreshold ||
      accYFiltered > accThreshold || accYFiltered < -accThreshold ||
      accZFiltered > accThreshold || accZFiltered < -accThreshold ||
      gyroXFiltered > gyroThreshold || gyroXFiltered < -gyroThreshold ||
      gyroYFiltered > gyroThreshold || gyroYFiltered < -gyroThreshold ||
      gyroZFiltered > gyroThreshold || gyroZFiltered < -gyroThreshold) {
    if (numSent < 0) {
      //Serial.println(F("Start of action"));
      numSent = 0;
    }
  }

  if (numSent >= 0) {
  #if 1
    Serial.print("count:"); Serial.print(numSent);
    Serial.print(",accXF:"); Serial.print(accXFiltered);
    Serial.print(",accYF:"); Serial.print(accYFiltered);
    Serial.print(",accZF:"); Serial.print(accZFiltered);
//    Serial.println();
  #endif
  
  #if 1
    Serial.print(",gyroXF:"); Serial.print(gyroXFiltered);
    Serial.print(",gyroYF:"); Serial.print(gyroYFiltered);
    Serial.print(",gyroZF:"); Serial.print(gyroZFiltered);
    Serial.println();
  #endif

    // send
    numSent++;

    if(numSent == numToSend) {
      numSent = -1;
    }
  }
  delay(10);
}

void calculateErrors() {
  int numSamples = 200;
  int count = 0;

  for (int i = 0; i < numSamples; i++) {
    while (i2cRead(ACC_REG, i2cData, 6));
    accX = (int16_t)((i2cData[0] << 8) | i2cData[1]) * ACC_SCALE;
    accY = (int16_t)((i2cData[2] << 8) | i2cData[3]) * ACC_SCALE;
    accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]) * ACC_SCALE;

    accXErr += accX;
    accYErr += accY;
    accZErr += accZ;
  
    while (i2cRead(GYRO_REG, i2cData, 6));
    gyroX = (int16_t)((i2cData[0] << 8) | i2cData[1]) * GYRO_SCALE;
    gyroY = (int16_t)((i2cData[2] << 8) | i2cData[3]) * GYRO_SCALE;
    gyroZ = (int16_t)((i2cData[4] << 8) | i2cData[5]) * GYRO_SCALE;

    gyroXErr += gyroX;
    gyroYErr += gyroY;
    gyroZErr += gyroZ;

    delay(10);
  }

  accXErr /= numSamples;
  accYErr /= numSamples;
  accZErr /= numSamples;
  
  gyroXErr /= numSamples;
  gyroYErr /= numSamples;
  gyroZErr /= numSamples;

#if 1
  Serial.println(accXErr);
  Serial.println(accYErr);
  Serial.println(accZErr);
  Serial.println(gyroXErr);
  Serial.println(gyroYErr);
  Serial.println(gyroZErr);
  delay(3000);
#endif
}

uint8_t i2cWrite(uint8_t registerAddress, uint8_t data, bool sendStop) {
  return i2cWrite(registerAddress, &data, 1, sendStop); // Returns 0 on success
}

uint8_t i2cWrite(uint8_t registerAddress, uint8_t *data, uint8_t length, bool sendStop) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(registerAddress);
  Wire.write(data, length);
  uint8_t rcode = Wire.endTransmission(sendStop); // Returns 0 on success
  if (rcode) {
    Serial.print(F("i2cWrite failed: "));
    Serial.println(rcode);
  }
  return rcode; // See: http://arduino.cc/en/Reference/WireEndTransmission
}

uint8_t i2cRead(uint8_t registerAddress, uint8_t *data, uint8_t nbytes) {
  uint32_t timeOutTimer;
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(registerAddress);
  uint8_t rcode = Wire.endTransmission(false); // Don't release the bus
  if (rcode) {
    Serial.print(F("i2cRead failed: "));
    Serial.println(rcode);
    return rcode; // See: http://arduino.cc/en/Reference/WireEndTransmission
  }
  Wire.requestFrom(IMU_ADDR, nbytes, (uint8_t)true); // Send a repeated start and then release the bus after reading
  for (uint8_t i = 0; i < nbytes; i++) {
    if (Wire.available())
      data[i] = Wire.read();
    else {
      timeOutTimer = micros();
      while (((micros() - timeOutTimer) < I2C_TIMEOUT) && !Wire.available());
      if (Wire.available())
        data[i] = Wire.read();
      else {
        Serial.println(F("i2cRead timeout"));
        return 5; // This error value is not already taken by endTransmission
      }
    }
  }
  return 0; // Success
}
