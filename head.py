import smbus
import time

# Configure the I2C bus
bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi Model B+

# Address of the accelerometer sensor
accelerometer_address = 0x68

# Register addresses for accelerometer data
accelerometer_x = 0x3B
accelerometer_y = 0x3D
accelerometer_z = 0x3F

# Constants
acceleration_scale = 16384.0  # Specific to the accelerometer used

# Initialize velocity variables
velocity_x = 0.0
velocity_y = 0.0
velocity_z = 0.0

# Sample rate (adjust as needed)
sample_rate = 0.1  # Example: 0.1 seconds between readings

def read_acceleration(register):
    high_byte = bus.read_byte_data(accelerometer_address, register)
    low_byte = bus.read_byte_data(accelerometer_address, register + 1)
    value = (high_byte << 8) | low_byte
    if value & (1 << 15):
        value -= 1 << 16
    return value / acceleration_scale

try:
    while True:
        # Read acceleration values
        accel_x = read_acceleration(accelerometer_x)
        accel_y = read_acceleration(accelerometer_y)
        accel_z = read_acceleration(accelerometer_z)

        # Integrate acceleration to get velocity (trapezoidal rule)
        velocity_x += accel_x * sample_rate
        velocity_y += accel_y * sample_rate
        velocity_z += accel_z * sample_rate

        # Display or use the velocity data as needed
        print(f"Velocity (X): {velocity_x}, Velocity (Y): {velocity_y}, Velocity (Z): {velocity_z}")

        # Adjust sample rate based on your requirements
        time.sleep(sample_rate)

except KeyboardInterrupt:
    print("Measurement stopped by the user")
