import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the BCM pin number for the buzzer
buzzer_pin = 17

# Set the GPIO pin as an output
GPIO.setup(buzzer_pin, GPIO.OUT)

def play_and_stop_buzzer():
    # Turn on the buzzer
    GPIO.output(buzzer_pin, GPIO.HIGH)
    
    # Play for 1 second
    time.sleep(2)  
    
    # Turn off the buzzer
    GPIO.output(buzzer_pin, GPIO.LOW)
    time.sleep(2)  # Wait for 1 second

try:
    while True:
        # Play and stop the buzzer every second
        play_and_stop_buzzer()

except KeyboardInterrupt:
    # Handle keyboard interrupt
    pass

finally:
    # Clean up GPIO on exit
    GPIO.cleanup()
