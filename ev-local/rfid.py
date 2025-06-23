from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Place your RFID card near the reader...")
    id, text = reader.read()
    print(f"RFID ID: {id}")
    print(f"Data on card: {text.strip()}")
finally:
    print("Cleaning up...")

