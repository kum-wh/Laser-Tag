// Adapted from https://github.com/Arduino-IRremote/Arduino-IRremote/blob/master/examples/SimpleReceiver/SimpleReceiver.ino

#define PLAYER_NUM 1

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

bool gReverseDirection = false;
CRGBPalette16 gPal;

void setup() {
  Serial.begin(115200);
  numLights = NUM_LEDS;
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  if (PLAYER_NUM == 1) {
    gPal = CRGBPalette16(CRGB::Black, CRGB::Red, CRGB::Yellow, CRGB::White);;
  } else {
    gPal = CRGBPalette16(CRGB::Black, CRGB::Blue, CRGB::Green, CRGB::White);
  }
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
      if (handshakeSuccess) {
        sendVestPacket();
      }
      
//      Serial.print("You got shot by player ");
//      Serial.println(IrReceiver.decodedIRData.address);
      numLights--;
      
      if (numLights < 0) {
        numLights = NUM_LEDS;
        onAllLEDs();
      } else {
        for (int i = 0; i < 20; i++) {
          random16_add_entropy( random());
          Fire2012WithPalette(); // run simulation frame, using palette colors
          FastLED.show(); // display this frame
          FastLED.delay(1000 / 60);
        }
        updateLEDs();
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

void updateLEDs() {
  FastLED.clear();
  for (int i = 0; i < NUM_LEDS; i++) {
    if (i < numLights) {
      if (PLAYER_NUM == 1) {
        leds[i] = CRGB::Red;
      } else {
        leds[i] = CRGB::Blue;
      }
    } else {
      leds[i] = CRGB::Black;
    }
  }
  FastLED.show();
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

// Fire2012 by Mark Kriegsman, July 2012
// as part of "Five Elements" shown here: http://youtu.be/knWiGsmgycY
//// 
// This basic one-dimensional 'fire' simulation works roughly as follows:
// There's a underlying array of 'heat' cells, that model the temperature
// at each point along the line.  Every cycle through the simulation, 
// four steps are performed:
//  1) All cells cool down a little bit, losing heat to the air
//  2) The heat from each cell drifts 'up' and diffuses a little
//  3) Sometimes randomly new 'sparks' of heat are added at the bottom
//  4) The heat from each cell is rendered as a color into the leds array
//     The heat-to-color mapping uses a black-body radiation approximation.
//
// Temperature is in arbitrary units from 0 (cold black) to 255 (white hot).
//
// This simulation scales it self a bit depending on NUM_LEDS; it should look
// "OK" on anywhere from 20 to 100 LEDs without too much tweaking. 
//
// I recommend running this simulation at anywhere from 30-100 frames per second,
// meaning an interframe delay of about 10-35 milliseconds.
//
// Looks best on a high-density LED setup (60+ pixels/meter).
//
//
// There are two main parameters you can play with to control the look and
// feel of your fire: COOLING (used in step 1 above), and SPARKING (used
// in step 3 above).
//
// COOLING: How much does the air cool as it rises?
// Less cooling = taller flames.  More cooling = shorter flames.
// Default 55, suggested range 20-100 
#define COOLING  55

// SPARKING: What chance (out of 255) is there that a new spark will be lit?
// Higher chance = more roaring fire.  Lower chance = more flickery fire.
// Default 120, suggested range 50-200.
#define SPARKING 120


void Fire2012WithPalette()
{
// Array of temperature readings at each simulation cell
  static uint8_t heat[NUM_LEDS];

  // Step 1.  Cool down every cell a little
    for( int i = 0; i < NUM_LEDS; i++) {
      heat[i] = qsub8( heat[i],  random8(0, ((COOLING * 10) / NUM_LEDS) + 2));
    }
  
    // Step 2.  Heat from each cell drifts 'up' and diffuses a little
    for( int k= NUM_LEDS - 1; k >= 2; k--) {
      heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2] ) / 3;
    }
    
    // Step 3.  Randomly ignite new 'sparks' of heat near the bottom
    if( random8() < SPARKING ) {
      int y = random8(7);
      heat[y] = qadd8( heat[y], random8(160,255) );
    }

    // Step 4.  Map from heat cells to LED colors
    for( int j = 0; j < NUM_LEDS; j++) {
      // Scale the heat value from 0-255 down to 0-240
      // for best results with color palettes.
      uint8_t colorindex = scale8( heat[j], 240);
      CRGB color = ColorFromPalette( gPal, colorindex);
      int pixelnumber;
      if( gReverseDirection ) {
        pixelnumber = (NUM_LEDS-1) - j;
      } else {
        pixelnumber = j;
      }
      leds[pixelnumber] = color;
    }
}
