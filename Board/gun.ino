// Adapted from https://github.com/Arduino-IRremote/Arduino-IRremote/blob/master/examples/SimpleSender/SimpleSender.ino

#define PLAYER_NUM 2

#define IR_SEND_PIN 3
#define BUTTON_PIN  2

#define GLOVE_BEETLE 3
#define GUN_BEETLE 4
#define VEST_BEETLE 5

#define ACK_TIMEOUT 100

#include <Arduino.h>
#include <IRremote.hpp>
#include <FastLED.h>

#define NUM_LEDS   6
#define DATA_PIN   5
#define BRIGHTNESS 2

uint16_t sAddress = PLAYER_NUM;
uint8_t sCommand = 1;
uint8_t sRepeats = 0;

volatile bool isShooting = false;
int numBullets;

volatile long prevTime;
bool receivedFirstHS = false;
bool handshakeSuccess = false;

CRGB leds[NUM_LEDS];

struct GunPacket {
  char packetID = 'G';
  uint8_t pn = PLAYER_NUM;
  char padding[18] = {0};
};

struct ACKPacket {
  char packetID = 'A';
  uint8_t pn = PLAYER_NUM;
  char padding[18] = {0};
};

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), shoot, FALLING);
  numBullets = NUM_LEDS;
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  onAllLEDs();
  IrSender.begin();
  prevTime = millis();
}

void shoot() {
  static unsigned long lastTime = 0;
  unsigned long currTime = millis();
  if (currTime - lastTime > 250) 
  {
    isShooting = true;
    lastTime = currTime;
  }
}

void loop() {
  if (receivedFirstHS && !handshakeSuccess) { 
      long currTime = millis();
      if(currTime - prevTime >= ACK_TIMEOUT) { 
        sendACKPacket();
        prevTime = currTime;
      }
  } 
  
  if (isShooting) {
    IrSender.sendNEC(sAddress, sCommand, sRepeats);
    isShooting = false;
    numBullets--;
    
    if (numBullets < 0) {
      numBullets = NUM_LEDS;
      onAllLEDs();
    } else {
      offOneLED();
    }

    if (handshakeSuccess) {
      sendGunPacket();
    }
    
//    Serial.println("Button press detected");
//    Serial.print(numBullets);
//    Serial.println(" bullets left");
  
    delay(100); // delay must be greater than 5 ms (RECORD_GAP_MICROS), otherwise the receiver sees it as one long signal
  }
}

void serialEvent() {
  int msg = Serial.read();
  if (msg == 'H') {
      receivedFirstHS = true;
      handshakeSuccess = false;
  } else if (msg == 'A') {  
      handshakeSuccess = true;
  } 
}

void sendGunPacket() {
  GunPacket packet;
  Serial.write((byte*)&packet, sizeof(packet));
}

void sendACKPacket() {
  ACKPacket packet;
  Serial.write((byte*)&packet, sizeof(packet));
}

void offOneLED() {
  if (numBullets < NUM_LEDS) {
    leds[numBullets] = CRGB::Black;
    FastLED.show();
  }
}

void onAllLEDs() {
  FastLED.clear();
  for (int i = 0; i < NUM_LEDS; i++) {
    if (PLAYER_NUM == 1) {
      leds[i] = CRGB::Red;
    } else {
      leds[i] = CRGB::Blue;
    }
  }
  FastLED.show();
}
