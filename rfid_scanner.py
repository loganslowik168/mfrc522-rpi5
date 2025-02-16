import mfrc522
import signal
import time

continue_reading = True

def uidToString(uid):
    return ''.join(format(i, '02X') for i in reversed(uid))

def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False

signal.signal(signal.SIGINT, end_read)
MIFAREReader = mfrc522.mfrc522()

def scan_rfid(mode="once", time_limit=10, match_uid=None):
    """
    Scanning Modes:
    - "once": Scan only once and return
    - "time": Scan repeatedly until `time_limit` seconds have elapsed
    - "match_or_time": Scan until a match is found OR `time_limit` seconds have elapsed
    - "match": Scan until a match is found, ignoring time
    - "first_match": Scan until any UID is found, then exit
    - "first_match_or_time": Scan until any UID is found OR `time_limit` seconds have elapsed
    """
    start_time = time.time()
    global continue_reading
    continue_reading = True
    
    while continue_reading:
        if mode == "once":
            continue_reading = False  # Exit after one scan
        
        if mode in ["time", "match_or_time", "first_match_or_time"] and (time.time() - start_time) > time_limit:
            print("Time limit reached.")
            break
        
        status, TagType = MIFAREReader.MFRC522Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            print("Card detected")
            status, uid = MIFAREReader.MFRC522_SelectTagSN()
            if status == MIFAREReader.MI_OK:
                uid_str = uidToString(uid)
                print("Card read UID:", uid_str)
                
                if mode in ["first_match", "first_match_or_time"]:
                    break
                
                if match_uid and uid_str == match_uid:
                    print("Match found!")
                    break
                
                if mode == "once":
                    break
        
        time.sleep(0.5)  # Slight delay to prevent excessive polling

# Example usages:
# scan_rfid(mode="once")  # Scan only once
# scan_rfid(mode="time", time_limit=10)  # Scan until 10 seconds pass
# scan_rfid(mode="match_or_time", time_limit=10, match_uid="12345678")  # Scan until match or time runs out
# scan_rfid(mode="match", match_uid="12345678")  # Scan indefinitely until a match is found
# scan_rfid(mode="first_match")  # Scan until any UID is found
# scan_rfid(mode="first_match_or_time", time_limit=10)  # Scan until any UID is found or time runs out
