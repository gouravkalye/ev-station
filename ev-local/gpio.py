import subprocess
import time

def start_charger():
    print("Turning relay ON")
    subprocess.run(['sudo', 'raspi-gpio', 'set', '4', 'op', 'dl'])

def stop_charger():
    print("Turning relay OFF")
    subprocess.run(['sudo', 'raspi-gpio', 'set', '4', 'op', 'dh'])
