import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS object
ads = ADS1115(i2c)

# Create a single-ended input on channel 0
chan = AnalogIn(ads, ADS1115.P0)

while True:
    print("Voltage: {:.3f} V".format(chan.voltage))
    time.sleep(1)
