from mfrc522 import scan_rfid


scan_rfid(mode='first_match_or_time', time_limit=5)


# # Example usages:
# scan_rfid(mode="once")  # Scan only once
# scan_rfid(mode="time", time_limit=10)  # Scan until 10 seconds pass
# scan_rfid(mode="match_or_time", time_limit=10, match_uid="12345678")  # Scan until match or time runs out
# scan_rfid(mode="match", match_uid="12345678")  # Scan indefinitely until a match is found
# scan_rfid(mode="first_match")  # Scan until any UID is found
# scan_rfid(mode="first_match_or_time", time_limit=10)  # Scan until any UID is found or time runs out