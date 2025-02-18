from gpiozero import DigitalInputDevice
from time import sleep

PININ = 24  # Input pin to be checked

# Create a DigitalInputDevice object for the input pin
gpioPin = DigitalInputDevice(PININ)

try:
    while True:
        if gpioPin.value:  # Check if pin is high (active)
            print("Pin 24 is active (HIGH).")
        else:
            print("Pin 24 is inactive (LOW).")
        
        sleep(0.05)  # Sleep for 50 milliseconds (0.05 seconds)

except KeyboardInterrupt:
    print("Program interrupted. Exiting...")
