
import re
import json
import time
import serial
import urllib.request

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200


def read_sensors():
    readings = {}

    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as esp:
        # ESP32 may reset when serial port opens
        time.sleep(2)

        deadline = time.monotonic() + 20

        while time.monotonic() < deadline:
            line = esp.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            patterns = {
                "soil_raw": r"Soil Moisture \(RAW\):\s*(\d+)",
                "front": r"Front LDR:\s*(\d+)",
                "back": r"Back LDR:\s*(\d+)",
                "left": r"Left LDR:\s*(\d+)",
                "right": r"Right LDR:\s*(\d+)",
            }

            for name, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    readings[name] = int(match.group(1))

            if all(key in readings for key in patterns):
                return readings

    raise RuntimeError("Could not read all required sensors")


def interpret_plant_state(data):
    soil = data["soil_raw"]

    # Preliminary thresholds based on earlier experiments
    if soil >= 2200:
        soil_state = "POSSIBLY_DRY"
        soil_description = (
            "My soil may be dry. I might need water."
        )
    elif soil <= 1700:
        soil_state = "POSSIBLY_MOIST"
        soil_description = (
            "My soil appears to have enough moisture."
        )
    else:
        soil_state = "UNCERTAIN"
        soil_description = (
            "My soil moisture level is uncertain."
        )

    return {
        "soil_state": soil_state,
        "soil_description": soil_description,
        "soil_raw": soil,
        "light_readings": {
            "front": data["front"],
            "back": data["back"],
            "left": data["left"],
            "right": data["right"],
        },
        "light_condition": "NOT_CALIBRATED",
        "temperature": None,
        "humidity": None,
    }


def ask_leafy(state, question):
    prompt = f"""
CURRENT VERIFIED SENSOR CONTEXT:
{json.dumps(state)}

USER QUESTION:
{question}

INSTRUCTIONS:
- Answer using only the supplied sensor context.
- The soil classification is preliminary, not certain.
- The light readings are raw and not calibrated.
- Temperature and humidity are unavailable.
- Never invent sensor readings.
- Never claim to have watered or moved.
- Reply in English using 1-2 short friendly sentences.

LEAFY:
"""

    payload = {
        "model": "leafy",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 80
        }
    }

    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)

    return result["response"].strip()


print("Reading real sensors from ESP32...")

try:
    raw_data = read_sensors()
    plant_state = interpret_plant_state(raw_data)

    print("\nReal Sensor Readings:")
    print(json.dumps(raw_data, indent=2))

    print("\nInterpreted Plant State:")
    print(json.dumps(plant_state, indent=2))

    question = "How are you feeling today?"
    print("\nQuestion:", question)

    answer = ask_leafy(plant_state, question)
    print("Leafy:", answer)

except (serial.SerialException, OSError, RuntimeError) as error:
    print("Error:", error)
