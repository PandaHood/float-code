#define DIR_PIN  8
#define STEP_PIN 9

#define STEPS_PER_REV 200
#define STEPS_90 (STEPS_PER_REV / 4)

bool running = false;
bool forward = true;
int stepDelayUs = 1000;

void setup() {
  Serial.begin(9600);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  digitalWrite(STEP_PIN, LOW);
  digitalWrite(DIR_PIN, HIGH);
  Serial.println("Arduino Ready");
}

void checkSerial() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();

    if (cmd == "E") {
      running = true;
      Serial.println("Motor enabled");
    } else if (cmd == "F") {
      running = true;
      forward = true;
      digitalWrite(DIR_PIN, HIGH);
      Serial.println("Moving forward");
    } else if (cmd == "B") {
      running = true;
      forward = false;
      digitalWrite(DIR_PIN, LOW);
      Serial.println("Moving backward");
    } else if (cmd == "S") {
      running = false;
      Serial.println("Stopped");
    } else {
      Serial.println("Unknown command");
    }
  }
}

void loop() {
  checkSerial();

  if (running) {
    // Take one 90 degree rotation then pause 1 second
    for (int i = 0; i < STEPS_90; i++) {
      if (Serial.available()) {
        checkSerial();
        if (!running) return;
      }
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(stepDelayUs);
      digitalWrite(STEP_PIN, LOW);
      delayMicroseconds(stepDelayUs);
    }

    if (running) {
      Serial.println("90 degree rotation complete");
      unsigned long pauseStart = millis();
      while (millis() - pauseStart < 1000) {
        checkSerial();  // keep checking during pause
      }
    }
  }
}
