# Required files
The actual repo only needs the  `mfrc522.py` files.  See `main.py` or the **Example Usage** in this README for the correct way to call the scanning function.
# Example usage
```python
from rfid_scanner import scan_rfid

# Example usages:
scan_rfid(mode="once")  # Scan only once
scan_rfid(mode="time", time_limit=10)  # Scan until 10 seconds pass
scan_rfid(mode="match_or_time", time_limit=10, match_uid="12345678")  # Scan until match or time runs out
scan_rfid(mode="match", match_uid="12345678")  # Scan indefinitely until a match is found
scan_rfid(mode="first_match")  # Scan until any UID is found
scan_rfid(mode="first_match_or_time", time_limit=10)  # Scan until any UID is found or time runs out
scan_rfid(mode="forever")  # Scan forever (must manually interrupt program to stop)

```


# Purpose
Made for the Holographic AI Assistant/Associate
# Resources
https://github.com/danjperron/MFRC522-python

https://github.com/mab5vot9us9a/MFRC522-python/blob/master/MFRC522.py 


# NOTE FOR LOGAN FOR E-WEEK
**Connect Johnathon to pin 23**