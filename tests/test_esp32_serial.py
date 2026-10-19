
import os
import sys
import time

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.sensors.esp32_serial import ESP32SerialReader


def main():
    reader = ESP32SerialReader()

    print("Reading real ESP32 sensor data...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            data = reader.read_data()

            if data:
                print("\nReceived sensor data:")
                for key, value in data.items():
                    print(f"{key}: {value}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        reader.close()


if __name__ == "__main__":
    main()
