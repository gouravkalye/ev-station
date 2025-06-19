import time
import math
from smbus2 import SMBus

# Constants for ADS1115
ADS1115_ADDRESS = 0x48
CONVERSION_REG = 0x00
CONFIG_REG = 0x01
GAIN = 0x0400  # Gain = +/- 2.048V
MUX_AIN0 = 0x4000  # AIN0
MODE_SINGLE = 0x0100
DR_860SPS = 0x00E0  # 860 samples per second
CONFIG_OS_SINGLE = 0x8000
CONFIG_DEFAULT = CONFIG_OS_SINGLE | MUX_AIN0 | GAIN | MODE_SINGLE | DR_860SPS | 0x0003

# Sensor and voltage config
SAMPLES = 300
V_REF = 2.048
ADC_RES = 32768.0
ACS_SENSITIVITY = 0.100  # V/A (for ACS712-20A)
VOLTAGE = 230.0

bus = SMBus(1)

def read_adc():
    bus.write_i2c_block_data(ADS1115_ADDRESS, CONFIG_REG, [(CONFIG_DEFAULT >> 8) & 0xFF, CONFIG_DEFAULT & 0xFF])
    time.sleep(0.002)
    data = bus.read_i2c_block_data(ADS1115_ADDRESS, CONVERSION_REG, 2)
    raw = (data[0] << 8) | data[1]
    return raw - 65536 if raw > 32767 else raw

def calibrate_offset(samples=300):
    total = 0
    for _ in range(samples):
        voltage = (read_adc() * V_REF) / ADC_RES
        total += voltage
    return total / samples

def get_rms_current(offset, samples=SAMPLES):
    sum_sq = 0
    for _ in range(samples):
        voltage = (read_adc() * V_REF) / ADC_RES
        adjusted = voltage - offset
        sum_sq += adjusted ** 2
    vrms = math.sqrt(sum_sq / samples)
    return vrms / ACS_SENSITIVITY

def calculate_power(current):
    return current * VOLTAGE

def calculate_energy(power, duration_seconds):
    return power * (duration_seconds / 3600.0)

def main():
    energy_Wh = 0
    interval = 1
    print("Calibrating offset... Ensure no load is connected.")
    offset = calibrate_offset()
    print(f"Calibrated offset: {offset:.4f} V")
    print("Measuring AC current and power. Press Ctrl+C to stop.")
    try:
        while True:
            current = get_rms_current(offset)
            power = calculate_power(current)
            energy_Wh += calculate_energy(power, interval)
            print(f"Current: {current:.2f} A | Power: {power:.1f} W | Energy: {energy_Wh:.3f} Wh")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMeasurement stopped.")

if __name__ == "__main__":
    main()
