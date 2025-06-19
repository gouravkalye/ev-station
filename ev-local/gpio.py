import subprocess
import time


print("Turning relay ON")
subprocess.run(['sudo', 'raspi-gpio', 'set', '4', 'op', 'dl'])
time.sleep(3)

print("Turning relay OFF")
subprocess.run(['sudo', 'raspi-gpio', 'set', '4', 'op', 'dh'])