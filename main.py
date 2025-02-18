from gpiozero import DigitalOutputDevice, DigitalInputDevice

from mfrc522 import scan_rfid
from dataclasses import dataclass
from time import sleep

@dataclass
class Tag:
    color: str
    uid: str
    pinout_level: int

# array of tags for demo at UAH E-Week 2025
tags = [Tag("Blue",'0E4845C3',1), Tag("White",'126DAD00',0)]
# pin out for RFID reading
PINOUT = 23
PININ = 24

gpioPinOut = DigitalOutputDevice(PINOUT)
#gpioPinIn = DigitalInputDevice(PININ)

# global that holds the most recent scan
prior_recent = None
recent = None


def set_pin(pin, state):
    if state == 1:
        # print("Pin on")
        gpioPinOut.on()
    elif state == 0:
        # print("Pin off")
        gpioPinOut.off()
    else:
        print("Invalid pin state.  Choose 1 for high or 0 for low.")
def read_pin(pin):
    print(f"Pin {pin} = {gpioPinIn.value}")  # Print raw value of pin
    if gpioPinIn.value:
        return True
    else:
        return False

try:
    while True:
        uid = scan_rfid(mode='first_match')
        for tag in tags:
            if tag.uid == uid:
                # print(f"Match on uid {uid}")
                prior_recent = recent
                recent = tag.pinout_level
        sleep(0.5)  # Slight delay to prevent excessive polling

        # if change in most recent card read
        if recent != prior_recent:
            print(f"Setting pin {PINOUT} to {recent}")
            set_pin(PINOUT, recent)

        # update pinin reading
        #print(f"Output pin is {'on' if read_pin(PININ) else 'off'}!")
except KeyboardInterrupt:
    # this part doesn't work right now but I can't worry about it tonight.
    # for now if you need to terminate the program you have to kill the process manually
    print("Received keyboard interrupt from reading function.  Terminating program.")
    


# # Example usages:
# scan_rfid(mode="once")  # Scan only once
# scan_rfid(mode="time", time_limit=10)  # Scan until 10 seconds pass
# scan_rfid(mode="match_or_time", time_limit=10, match_uid="12345678")  # Scan until match or time runs out
# scan_rfid(mode="match", match_uid="12345678")  # Scan indefinitely until a match is found
# scan_rfid(mode="first_match")  # Scan until any UID is found
# scan_rfid(mode="first_match_or_time", time_limit=10)  # Scan until any UID is found or time runs out
# scan_rfid(mode="forever")  # Scan forever (must manually interrupt program to stop)