#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "Utsav";
const char* password = "12345678";

ESP8266WebServer server(80);

// =====================================================
// SILK BOARD JUNCTION (Route A)
// =====================================================

#define RED_A    D1
#define GREEN_A  D2

// =====================================================
// BTM LAYOUT JUNCTION (Route B)
// =====================================================

#define RED_B    D5
#define GREEN_B  D6

// =====================================================
// JAYADEVA JUNCTION (Route C)
// =====================================================

#define RED_C    D7
#define GREEN_C  D0

// =====================================================
// BUZZER
// =====================================================

#define BUZZER   D4

// =====================================================
// BEEP BUZZER
// Beeps once for 1 second and automatically stops
// =====================================================

void beepBuzzer()
{
  digitalWrite(BUZZER, HIGH);
  delay(1000);
  digitalWrite(BUZZER, LOW);
}

// =====================================================
// ALL RED
// =====================================================

void allRed()
{
  digitalWrite(RED_A, HIGH);
  digitalWrite(RED_B, HIGH);
  digitalWrite(RED_C, HIGH);

  digitalWrite(GREEN_A, LOW);
  digitalWrite(GREEN_B, LOW);
  digitalWrite(GREEN_C, LOW);
}

// =====================================================
// ROUTE A
// SILK BOARD
// =====================================================

void corridorA()
{
  allRed();

  digitalWrite(RED_A, LOW);
  digitalWrite(GREEN_A, HIGH);

  beepBuzzer();

  server.send(
    200,
    "text/plain",
    "Silk Board Corridor Activated"
  );
}

// =====================================================
// ROUTE B
// BTM
// =====================================================

void corridorB()
{
  allRed();

  digitalWrite(RED_B, LOW);
  digitalWrite(GREEN_B, HIGH);

  beepBuzzer();

  server.send(
    200,
    "text/plain",
    "BTM Corridor Activated"
  );
}

// =====================================================
// ROUTE C
// JAYADEVA
// =====================================================

void corridorC()
{
  allRed();

  digitalWrite(RED_C, LOW);
  digitalWrite(GREEN_C, HIGH);

  beepBuzzer();

  server.send(
    200,
    "text/plain",
    "Jayadeva Corridor Activated"
  );
}

// =====================================================
// NORMAL MODE
// =====================================================

void normalMode()
{
  digitalWrite(BUZZER, LOW);

  digitalWrite(RED_A, LOW);
  digitalWrite(GREEN_A, HIGH);

  digitalWrite(RED_B, HIGH);
  digitalWrite(GREEN_B, LOW);

  digitalWrite(RED_C, HIGH);
  digitalWrite(GREEN_C, LOW);

  server.send(
    200,
    "text/plain",
    "Normal Mode"
  );
}

// =====================================================
// STATUS
// =====================================================

void status()
{
  server.send(
    200,
    "application/json",
    "{\"status\":\"online\"}"
  );
}

// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  pinMode(RED_A, OUTPUT);
  pinMode(GREEN_A, OUTPUT);

  pinMode(RED_B, OUTPUT);
  pinMode(GREEN_B, OUTPUT);

  pinMode(RED_C, OUTPUT);
  pinMode(GREEN_C, OUTPUT);

  pinMode(BUZZER, OUTPUT);

  digitalWrite(BUZZER, LOW);

  WiFi.begin(ssid, password);

  Serial.println();
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/normal", normalMode);

  server.on("/emergencyA", corridorA);
  server.on("/emergencyB", corridorB);
  server.on("/emergencyC", corridorC);

  server.on("/status", status);

  server.begin();

  Serial.println("Server Started");

  normalMode();
}

// =====================================================
// LOOP
// =====================================================

void loop()
{
  server.handleClient();
}
