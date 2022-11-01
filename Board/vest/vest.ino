// Adapted from https://github.com/Arduino-IRremote/Arduino-IRremote/blob/master/examples/SimpleReceiver/SimpleReceiver.ino

#define PLAYER_NUM 2

#define GLOVE_BEETLE 3
#define GUN_BEETLE 4
#define VEST_BEETLE 5

#define ACK_TIMEOUT 100

#define DECODE_NEC // Specify which protocol(s) should be used for decoding. If no protocol is defined, all protocols are active.
#define IR_RECEIVE_PIN 2 

#include <Arduino.h>
#include <IRremote.hpp>
#include <FastLED.h>

#define NUM_LEDS   10
#define DATA_PIN   3
#define BRIGHTNESS 10

CRGB leds[NUM_LEDS];
int numLights;

volatile long prevTime;
bool receivedFirstHS = false;
bool handshakeSuccess = false;

struct VestPacket {
  char packetID = 'V';
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
  numLights = NUM_LEDS;
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  onAllLEDs();
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
  prevTime = millis();
}

void loop() {
  if (receivedFirstHS && !handshakeSuccess) { 
      long currTime = millis();
      if(currTime - prevTime >= ACK_TIMEOUT) { 
        sendACKPacket();
        prevTime = currTime;
      }
  } 
  
  if (IrReceiver.decode()) {
//    IrReceiver.printIRResultShort(&Serial);
    
    if (IrReceiver.decodedIRData.protocol != NEC) {
//      Serial.println("Protocol is not NEC");
//      IrReceiver.printIRResultRawFormatted(&Serial, true);
      IrReceiver.resume();
      return;
    }
    
    IrReceiver.resume(); // Enable receiving of the next value

    if (IrReceiver.decodedIRData.address != PLAYER_NUM) {
//      Serial.print("You got shot by player ");
//      Serial.println(IrReceiver.decodedIRData.address);
      numLights--;
      
      if (numLights < 0) {
        numLights = NUM_LEDS;
        onAllLEDs();
      } else {
        offOneLED();
      }

      if (handshakeSuccess) {
        sendVestPacket();
      }
      
//    } else {
//      Serial.println("Can't shoot yourself!");
    }
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

void sendVestPacket() {
  VestPacket packet;
  Serial.write((byte*)&packet, sizeof(packet));
}

void sendACKPacket() {
  ACKPacket packet;
  Serial.write((byte*)&packet, sizeof(packet));
}

void offOneLED() {
  if (numLights < NUM_LEDS) {
    leds[numLights] = CRGB::Black;
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
