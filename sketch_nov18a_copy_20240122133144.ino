#include <stdarg.h>
#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, /*clock=*/14, /*data=*/12, U8X8_PIN_NONE);
ESP8266WiFiMulti WiFiMulti;
int wifiDotCount = 0;
int seqence = 0;


void setup() {
    u8g2.begin();
    Serial.begin(115200);
    Serial.println("");
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    print_osas("Init...");

    for (uint8_t t = 4; t > 0; t--) {
        Serial.printf("[SETUP] WAIT %d...\n", t);
        Serial.flush();
        delay(100);
    }

    WiFi.mode(WIFI_STA);
    WiFiMulti.addAP("@Reyee-s3E1D", "Mingchuan1948");
    WiFiMulti.addAP("StGeorgeResidence", "55Brooklyn");
    print_osas("Start Connecting..");
}

void blink(){
  digitalWrite(LED_BUILTIN, LOW);
  delay(1);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1);
}

void print_osas(const char* format, ...) {
    char mbuffer[128]; // Buffer to hold the formatted message
    va_list args;
    va_start(args, format);
    vsnprintf(mbuffer, sizeof(mbuffer), format, args);
    va_end(args);
    int len = strlen(mbuffer);
    int line = 1;
    char buffer[19]; // Buffer to hold each line of text

    // Print the entire message on the serial monitor
    Serial.println(mbuffer);
    blink();
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_7x14B_tr);

    for (int i = 0; i < len; i += 18) {
        strncpy(buffer, &mbuffer[i], 18); // Copy 14 characters from the message to the buffer
        buffer[18] = '\0'; // Null-terminate the buffer
        u8g2.drawStr(0, line * 14, buffer); // Draw the buffer to the screen at the correct line
        line++; // Move to the next line
    }
    u8g2.sendBuffer();
}

void loop() {
    if ((WiFiMulti.run() == WL_CONNECTED)) {
        wifiDotCount = 0;
        WiFiClient client;
        HTTPClient http;

        // print_osas("[HTTP] begin...");
        if (http.begin(client, "http://165.22.15.224:8000/status?seq=" + String(seqence) + "&name=arduino")) {
            // print_osas("[HTTP] GET...");
            int httpCode = http.GET();
            if (httpCode > 0) {
                // print_osas("[HTTP] GET... code: %d", httpCode);
                if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
                    String payload = http.getString();
                    if (payload != "") {
                      print_osas("%s", payload.c_str());
                    } else {
                      print_osas("None");
                    }
                }
            } else {
                print_osas("[HTTP] GET... failed, error: %s", http.errorToString(httpCode).c_str());
            }
            http.end();
        } else {
            print_osas("[HTTP] Unable to connect");
        }
    seqence++;
    delay(5000);
    } else {
      wifiDotCount = (wifiDotCount + 1) % 4;
      String dots = "";
      for (int i = 0; i < wifiDotCount; i++) {
          dots += ".";
      }
      print_osas("Connecting wifi.%s", dots);
      // print_osas("Connecting wifi." + String(std::string(wifiDotCount, '.')));
      delay(250);
    }
    
}