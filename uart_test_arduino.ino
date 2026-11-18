// UART Communication Test — Arduino side
// Wiring: Pi TX (GPIO14) → Arduino RX
//         Pi RX (GPIO15) → Arduino TX
//         Pi GND         → Arduino GND
// NOTE: use a logic level converter — Pi is 3.3V, Arduino is 5V

void setup() {
  Serial.begin(9600);
  while (!Serial);  // wait for serial to be ready
  Serial.println("Arduino ready");
}

void loop() {
  if (Serial.available()) {
    String received = Serial.readStringUntil('\n');
    received.trim();

    // Echo it straight back to the Pi
    Serial.println("Arduino received: " + received);
  }
}
