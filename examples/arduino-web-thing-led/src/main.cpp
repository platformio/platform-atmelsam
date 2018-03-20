/*
  WiFi Web Server LED control via web of things (e.g., iot.mozilla.org gateway)
  based on WiFi101.h example "Provisioning_WiFiWebServer.ino"

 A simple web server that lets you control an LED via the web.
 This sketch will print the IP address of your WiFi device (once connected)
 to the Serial monitor. From there, you can open that address in a web browser
 to turn on and off the onboard LED.

 You can also connect via the Things Gateway http-on-off-wifi-adapter.

 If the IP address of your shield is yourAddress:
 http://yourAddress/H turns the LED on
 http://yourAddress/L turns it off

 This example is written for a network using WPA encryption. For
 WEP or WPA, change the Wifi.begin() call accordingly.

 Circuit:
 * WiFi using Microchip (Atmel) WINC1500
 * LED attached to pin 1 (onboard LED) for SAMW25
 * LED attached to pin 6 for MKR1000

 created 25 Nov 2012
 by Tom Igoe

 updates: dh, kg 2018
 */

#include <Arduino.h>
#include <SPI.h>
#include <WiFi101.h>
#include <WiFiMDNSResponder.h>

#ifndef PIN_STATE_HIGH
#define PIN_STATE_HIGH HIGH
#endif
#ifndef PIN_STATE_LOW
#define PIN_STATE_LOW LOW
#endif


char mdnsName[] = "wifi101-XXXXXX"; // the MDNS name that the board will respond to
                                    // after WiFi settings have been provisioned.
// The -XXXXXX will be replaced with the last 6 digits of the MAC address.
// The actual MDNS name will have '.local' after the name above, so
// "wifi101-123456" will be accessible on the MDNS name "wifi101-123456.local".

byte mac[6];

WiFiServer server(80);

// Create a MDNS responder to listen and respond to MDNS name requests.
WiFiMDNSResponder mdnsResponder;

void printWiFiStatus();

void setup() {
  //Initialize serial:
  Serial.begin(9600);

  // check for the presence of the shield:
  Serial.print("Configuring WiFi shield/module...\n");
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // configure the LED pin for output mode
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.print("Starting in provisioning mode...\n");
  // Start in provisioning mode:
  //  1) This will try to connect to a previously associated access point.
  //  2) If this fails, an access point named "wifi101-XXXX" will be created, where XXXX
  //     is the last 4 digits of the boards MAC address. Once you are connected to the access point,
  //     you can configure an SSID and password by visiting http://wifi101/
  WiFi.beginProvision();

  while (WiFi.status() != WL_CONNECTED) {
    // wait while not connected

    // blink the led to show an unconnected status
    digitalWrite(LED_BUILTIN, PIN_STATE_HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, PIN_STATE_LOW);
    delay(500);
  }

  // connected, make the LED stay on
  digitalWrite(LED_BUILTIN, PIN_STATE_HIGH);

  WiFi.macAddress(mac);
  // Replace the XXXXXX in wifi101-XXXXXX with the last 6 digits of the MAC address.
  if (strcmp(&mdnsName[7], "-XXXXXX") == 0) {
    sprintf(&mdnsName[7], "-%.2X%.2X%.2X", mac[2], mac[1], mac[0]);
  }

  server.begin();

  // Setup the MDNS responder to listen to the configured name.
  // NOTE: You _must_ call this _after_ connecting to the WiFi network and
  // being assigned an IP address.
  if (!mdnsResponder.begin(mdnsName)) {
    Serial.println("Failed to start MDNS responder!");
    while(1);
  }

  Serial.print("Server listening at http://");
  Serial.print(mdnsName);
  Serial.println(".local/");

  // you're connected now, so print out the status:
  printWiFiStatus();
}

unsigned long lastPrint = 0;

void loop() {
  // Call the update() function on the MDNS responder every loop iteration to
  // make sure it can detect and respond to name requests.
  mdnsResponder.poll();

  // listen for incoming clients
  WiFiClient client = server.available();
  if (client) {
    Serial.println("new client");
    // an http request ends with a blank line
    String currentLine = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n') {
          if (currentLine.length() == 0) {
            // if the current line is blank, you got two newline characters in a row.
            // that's the end of the client HTTP request, so send a response:

            // send a standard http response header
            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: text/html");
            client.println("Connection: close");  // the connection will be closed after completion of the response
            client.println("Refresh: 5");  // refresh the page automatically every 5 sec
            client.println();
            client.println("<!DOCTYPE HTML>");
            client.println("<html>");

            // the content of the HTTP response follows the header:
            client.print("Click <a href=\"/H\">here</a> to turn the LED on<br>");
            client.print("Click <a href=\"/L\">here</a> turn the LED off<br>");

            client.println("</html>");
            // break out of the while loop:
            break;
          } else {
            currentLine = "";
          }
        }
        else if (c != '\r') {
          currentLine += c;
        }

        // Check to see if the client request was "GET /H" or "GET /L":
        if (currentLine.endsWith("GET /H")) {
          digitalWrite(LED_BUILTIN, PIN_STATE_HIGH);  // GET /H turns the LED on
        }
        if (currentLine.endsWith("GET /L")) {
          digitalWrite(LED_BUILTIN, PIN_STATE_LOW);  // GET /L turns the LED off
        }

      }
    }
    // give the web browser time to receive the data
    delay(1);

    // close the connection:
    client.stop();
    Serial.println("client disonnected");
  }
}

void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  Serial.print("MDNS Name: ");
  Serial.println(mdnsName);

  Serial.print("Mac: ");
  Serial.print(mac[5], HEX);
  Serial.print(":");
  Serial.print(mac[4], HEX);
  Serial.print(":");
  Serial.print(mac[3], HEX);
  Serial.print(":");
  Serial.print(mac[2], HEX);
  Serial.print(":");
  Serial.print(mac[1], HEX);
  Serial.print(":");
  Serial.println(mac[0], HEX);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
