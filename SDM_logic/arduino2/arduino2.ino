#include <Servo.h>
#include <string.h>

#define TRIG 2 // Ultrasonic sensor trigger pin
#define ECHO 3 // Ultrasonic sensor echo pin (PWM)

#define SERVO_BR 4   // Servo for Biodegradable & Recyclable waste bin
#define SERVO_BNR 5  // Servo for Biodegradable & Non-Recyclable waste bin
#define SERVO_NBR 6  // Servo for Non-Biodegradable & Recyclable waste bin
#define SERVO_NBNR 7 // Servo for Non-Biodegradable & Non-Recyclable waste bin

#define SERVO_LOW 9       // Lower servo in sorting mechanism
#define SERVO_UP 10       // Upper servo in sorting mechanism
#define SERVO_MID_FLAP 11 // Middle flap servo for waste direction

#define SERVO_LID 12       // Servo for Lid
#define PROXIMITY_OPEN 22  // To open main Lid
#define PROXIMITY_CLOSE 23 // To close main Lid

Servo lowerServo;   // Controls lower sorting mechanism
Servo upperServo;   // Controls upper sorting mechanism
Servo midflapServo; // Controls middle flap
Servo servo_br;     // Controls BR bin flap
Servo servo_bnr;    // Controls BNR bin flap
Servo servo_nbr;    // Controls NBR bin flap
Servo servo_nbnr;   // Controls NBNR bin flap
Servo servo_lid;    // Controls the Lid

int angleLower = 0;   // Starting position for lower servo
int angleUpper = 0;   // Starting position for upper servo
int anglemidflap = 0; // Starting position for mid flap
long updated_sensor_values[4] = {0, 0, 0, 0};

void setup()
{
  Serial.begin(9600); // Initialize serial communication
  while (!Serial)
  {
    ;
  } // Wait for serial connection to establish
  Serial.println("ARDUINO2"); // Initial handshake

  // Configure ultrasonic sensor pins
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // Configure proximity sensor
  pinMode(PROXIMITY_OPEN, INPUT);
  pinMode(PROXIMITY_CLOSE, INPUT);

  // Attach all servos to their respective pins
  lowerServo.attach(SERVO_LOW);
  upperServo.attach(SERVO_UP);
  midflapServo.attach(SERVO_MID_FLAP);
  servo_br.attach(SERVO_BR);
  servo_bnr.attach(SERVO_BNR);
  servo_nbr.attach(SERVO_NBR);
  servo_nbnr.attach(SERVO_NBNR);
  servo_lid.attach(SERVO_LID);

  // Set all servos to their initial positions
  lowerServo.write(angleLower);
  upperServo.write(angleUpper);
  midflapServo.write(anglemidflap);
  servo_br.write(0);
  servo_bnr.write(0);
  servo_nbr.write(0);
  servo_nbnr.write(0);
  servo_lid.write(0);
}

void update_distance(int n)
{
  delay(2000); // Allow time for trash to settle in bin

  // Ultrasonic sensor measurement sequence
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duration = pulseIn(ECHO, HIGH);  // Get echo duration
  long distance = duration * 0.034 / 2; // Convert duration to distance in cm
  updated_sensor_values[n] = distance;  // Store distance in array
}

void disk_reset()
{
  lowerServo.write(angleLower);
  upperServo.write(angleUpper);
}

void bio_ren()
{
  upperServo.write(45); // Set upper servo to 45 degrees
  delay(1000);
  lowerServo.write(0); // Set lower servo to 0 degrees
  delay(1000);

  midflapServo.write(90); // Open mid flap
  delay(3000);            // Wait for waste to fall
  midflapServo.write(0);  // Close mid flap
  delay(1000);
}

void bio_nonren()
{
  upperServo.write(135); // Set upper servo to 135 degrees
  delay(1000);
  lowerServo.write(0); // Set lower servo to 0 degrees
  delay(1000);

  midflapServo.write(90); // Open mid flap
  delay(3000);
  midflapServo.write(0); // Close mid flap
  delay(1000);
}

void nonbio_ren()
{
  upperServo.write(135); // Set upper servo to 135 degrees
  delay(1000);
  lowerServo.write(90); // Set lower servo to 90 degrees
  delay(1000);

  midflapServo.write(90); // Open mid flap
  delay(3000);
  midflapServo.write(0); // Close mid flap
  delay(1000);
}

void nonbio_nonren()
{
  upperServo.write(135); // Set upper servo to 135 degrees
  delay(1000);
  lowerServo.write(180); // Set lower servo to 180 degrees
  delay(1000);

  midflapServo.write(90); // Open mid flap
  delay(3000);
  midflapServo.write(0); // Close mid flap
  delay(1000);
}

void flush_trash_to_external_bin()
{
  // Open all bin flaps
  servo_br.write(90);
  servo_bnr.write(90);
  servo_nbr.write(90);
  servo_nbnr.write(90);

  delay(4000); // Wait for bins to empty

  // Close all bin flaps
  servo_br.write(0);
  servo_bnr.write(0);
  servo_nbr.write(0);
  servo_nbnr.write(0);
}

void close_lid()
{
  servo_lid.write(0); // Lid close
  delay(1000);
}

void open_lid()
{
  servo_lid.write(90); // Lid close
  delay(1000);
}

void loop()
{
  // Check for serial commands
  if (Serial.available() > 0)
  {
    //delay(1000);
    String message = Serial.readStringUntil('\n');
    //message.trim(); // Remove whitespace
    //Serial.println(message);

    if (message.equals("HANDSHAKE"))
    {
      Serial.println("ARDUINO2");
    }

    // Process different commands
    if (message.equals("BR"))
    {
      bio_ren();
      update_distance(0);
      disk_reset();
    }
    else if (message.equals("BNR"))
    {
      bio_nonren();
      update_distance(1);
      disk_reset();
    }
    else if (message.equals("NBR"))
    {
      nonbio_ren();
      update_distance(2);
      disk_reset();
    }
    else if (message.equals("NBNR"))
    {
      nonbio_nonren();
      update_distance(3);
      disk_reset();
    }
    else if (message.equals("GETD")) // Request bin levels
    {
      // Send all sensor values as comma-separated string
      Serial.print(updated_sensor_values[0]);
      Serial.print(",");
      Serial.print(updated_sensor_values[1]);
      Serial.print(",");
      Serial.print(updated_sensor_values[2]);
      Serial.print(",");
      Serial.println(updated_sensor_values[3]);
    }
    else if (message.equals("FLUSH")) // Empty all bins
    {
      flush_trash_to_external_bin();
    }
    else if (message.equals("RESTART"))
    {
      while (true)
      {
        if ((digitalRead(PROXIMITY_OPEN) == HIGH) && (digitalRead(PROXIMITY_CLOSE) == LOW))
        {
          open_lid();
        }
        else if ((digitalRead(PROXIMITY_CLOSE) == HIGH) && (digitalRead(PROXIMITY_OPEN) == LOW))
        {
          close_lid();
          break;
        }
        delay(1000);
      }
    }
  }
}
