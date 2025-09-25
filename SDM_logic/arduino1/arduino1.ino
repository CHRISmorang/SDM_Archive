// Pin definitions for CNC shield (X-axis)
#define DIR_PIN 5  // Direction pin
#define STEP_PIN 2 // Step pin
#define EN_PIN 8   // Enable pin (optional)

// Motor settings
#define STEPS_PER_REV 800                              // Steps per revolution for the stepper motor (change if needed)
#define DEGREE_TO_ROTATIONS(degrees) ((degrees) / 360) // Convert degrees to full rotations
#define STEP_DELAY_FAST 200                            // Step delay for fast forward motion (adjust for speed)
#define STEP_DELAY_SLOW 100                            // Step delay for slow return motion (adjust for speed)

void setup()
{
  // Set pins as outputs
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);

  // Enable the motor driver (LOW to enable, HIGH to disable)
  digitalWrite(EN_PIN, LOW); // Enable motor

  // Start serial communication for debugging
  Serial.begin(9600);
  while (!Serial)
  {
    ;
  } // Wait for serial connection to establish
  Serial.println("ARDUINO1"); // Send handshake signal
}

void loop()
{
  if (Serial.available() > 0)

  {
    //delay(1000);
    String command = Serial.readStringUntil('\n');
    //Serial.println(command+"+");

    // If the command is "run", start the motor sequence
    if (command == "HANDSHAKE")
    {
      Serial.println("ARDUINO1");
    }

    if (command == "COMPRESS")
    {
      // Move piston forward for 3600 degrees (10 rotations)
      //Serial.println(command);
      digitalWrite(DIR_PIN, LOW);                            // Set direction (HIGH for forward)
      moveMotor(DEGREE_TO_ROTATIONS(7200), STEP_DELAY_FAST); // Fast forward motion

      delay(1000); // Wait for 1 second before reversing direction

      // Move piston backward to return slowly

      digitalWrite(DIR_PIN, HIGH);                           // Set direction (LOW for reverse)
      moveMotor(DEGREE_TO_ROTATIONS(7200), STEP_DELAY_SLOW); // Slow return motion

      delay(1000);
    }
  } // Wait for 1 second before repeating
}

// Function to move the motor for the specified number of rotations
void moveMotor(int rotations, int stepDelay)
{
  int stepsToMove = rotations * STEPS_PER_REV; // Calculate total steps to move for the given rotations

  // Rotate the motor by sending step pulses
  for (int i = 0; i < stepsToMove; i++)
  {
    digitalWrite(STEP_PIN, HIGH); // Step pulse HIGH
    delayMicroseconds(stepDelay); // Delay for controlling motor speed
    digitalWrite(STEP_PIN, LOW);  // Step pulse LOW
    delayMicroseconds(stepDelay); // Delay for controlling motor speed
  }
}