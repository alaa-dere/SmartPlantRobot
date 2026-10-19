
import re
import serial


class ESP32SerialReader:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )

        self.last_block = {}
        self.in_block = False

    def read_data(self):
        while True:
            raw = self.serial.readline()
            if not raw:
                return None

            line = raw.decode(
                "utf-8", errors="replace"
            ).strip()

            if "SENSOR READINGS" in line:
                self.last_block = {}
                self.in_block = True
                continue

            if not self.in_block:
                continue

            if line.startswith("Soil Moisture (RAW):"):
                match = re.search(r":\s*(\d+)", line)
                if match:
                    self.last_block["soil_raw"] = int(match.group(1))

            elif line.startswith("BME280: NOT CONNECTED"):
                self.last_block["bme_connected"] = False

            elif line.startswith("Temperature:"):
                match = re.search(r":\s*(-?\d+(?:\.\d+)?)", line)
                if match:
                    self.last_block["temperature"] = float(match.group(1))
                    self.last_block["bme_connected"] = True

            elif line.startswith("Air Humidity:"):
                match = re.search(r":\s*(-?\d+(?:\.\d+)?)", line)
                if match:
                    self.last_block["humidity"] = float(match.group(1))

            elif line.startswith("Pressure:"):
                match = re.search(r":\s*(-?\d+(?:\.\d+)?)", line)
                if match:
                    self.last_block["pressure"] = float(match.group(1))

            elif line.startswith("Front LDR:"):
                self.last_block["ldr_front"] = int(line.split(":")[1])

            elif line.startswith("Back LDR:"):
                self.last_block["ldr_back"] = int(line.split(":")[1])

            elif line.startswith("Left LDR:"):
                self.last_block["ldr_left"] = int(line.split(":")[1])

            elif line.startswith("Right LDR:"):
                self.last_block["ldr_right"] = int(line.split(":")[1])

            elif line and set(line) == {"="}:
                self.in_block = False

                required = (
                    "soil_raw",
                    "ldr_front",
                    "ldr_back",
                    "ldr_left",
                    "ldr_right"
                )

                if all(k in self.last_block for k in required):
                    return self.last_block.copy()

    def close(self):
        if self.serial.is_open:
            self.serial.close()
