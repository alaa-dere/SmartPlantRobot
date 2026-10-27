
import os
import sys
import time
import threading
from collections import deque

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.sensors.esp32_serial import ESP32SerialReader
from src.emotions.emotion_controller import EmotionController
from src.display.oled_display import OLEDDisplay


# ======================================
# SOIL CONFIGURATION
# ======================================

# Temporary calibration values
SOIL_DRY_THRESHOLD = 2200
SOIL_WET_THRESHOLD = 2050


# ======================================
# TEMPERATURE CONFIGURATION
# ======================================

# Temporary thresholds
TEMP_HOT_THRESHOLD = 25.0
TEMP_NORMAL_THRESHOLD = 28.0


# ======================================
# LIGHT CONFIGURATION
# ======================================

# Enable only connected LDR sensors
LDR_ENABLED = {
    "ldr_front": True,
    "ldr_back": False,
    "ldr_left": True,
    "ldr_right": False
}

# Your current circuit:
# Higher ADC value = darker
# Lower ADC value = brighter
LIGHT_HIGHER_IS_BRIGHTER = False

LIGHT_DETECTION_ENABLED = True

# Temporary thresholds for testing
# Both active LDRs must be dark for NEEDS_LIGHT
LIGHT_DARK_THRESHOLD = 850

# One active LDR becoming bright can clear NEEDS_LIGHT
LIGHT_BRIGHT_THRESHOLD = 350

# Searching is not connected to motors yet
SIMULATE_SEARCHING = False


# ======================================
# STABILITY CONFIGURATION
# ======================================

STABLE_READINGS = 3
SENSOR_TIMEOUT = 10

# Shared Serial data
latest_data = None
last_received = 0
serial_error = None
data_version = 0

lock = threading.Lock()
stop_event = threading.Event()


# ======================================
# SERIAL READER THREAD
# ======================================

def read_sensors():
    global latest_data
    global last_received
    global serial_error
    global data_version

    reader = None

    try:
        reader = ESP32SerialReader()

        while not stop_event.is_set():
            data = reader.read_data()

            if data:
                with lock:
                    latest_data = data.copy()
                    last_received = time.monotonic()
                    data_version += 1

    except Exception as e:
        with lock:
            serial_error = str(e)

        print("Serial Error:", e, flush=True)

    finally:
        if reader:
            reader.close()


# ======================================
# PLANT STATE EVALUATOR
# ======================================

class PlantStateEvaluator:

    def __init__(self):
        self.soil_dry = None
        self.temp_high = False
        self.light_low = False

        self.dry_count = 0
        self.wet_count = 0

        self.hot_count = 0
        self.normal_count = 0

        self.low_light_count = 0
        self.good_light_count = 0

        self.light_history = deque(maxlen=3)
        self.light_average = None

    # ----------------------------------
    # SOIL MOISTURE
    # ----------------------------------

    def evaluate_soil(self, data):
        raw = data["soil_raw"]

        if raw >= SOIL_DRY_THRESHOLD:
            self.dry_count += 1
            self.wet_count = 0

        elif raw <= SOIL_WET_THRESHOLD:
            self.wet_count += 1
            self.dry_count = 0

        else:
            self.dry_count = 0
            self.wet_count = 0

        if self.dry_count >= STABLE_READINGS:
            self.soil_dry = True

        elif self.wet_count >= STABLE_READINGS:
            self.soil_dry = False

    # ----------------------------------
    # TEMPERATURE
    # ----------------------------------

    def evaluate_temperature(self, data):
        temp = data.get("temperature")

        if (
            not data.get("bme_connected", False)
            or temp is None
            or not (-40 <= temp <= 85)
        ):
            self.temp_high = False
            self.hot_count = 0
            self.normal_count = 0
            return

        if temp >= TEMP_HOT_THRESHOLD:
            self.hot_count += 1
            self.normal_count = 0

        elif temp <= TEMP_NORMAL_THRESHOLD:
            self.normal_count += 1
            self.hot_count = 0

        else:
            self.hot_count = 0
            self.normal_count = 0

        if self.hot_count >= STABLE_READINGS:
            self.temp_high = True

        elif self.normal_count >= STABLE_READINGS:
            self.temp_high = False

    # ----------------------------------
    # LIGHT SENSORS
    # ----------------------------------

    def evaluate_light(self, data):

        active_values = {
            name: data[name]
            for name, enabled in LDR_ENABLED.items()
            if enabled and name in data
        }

        if not active_values or not LIGHT_DETECTION_ENABLED:
            self.light_low = False
            self.light_average = None
            self.light_history.clear()
            return active_values

        # Select the brightest available direction.
        #
        # In your current circuit:
        # Lower RAW = Brighter
        # Higher RAW = Darker

        if LIGHT_HIGHER_IS_BRIGHTER:
            brightest_value = max(active_values.values())
            darkness_value = 4095 - brightest_value
        else:
            brightest_value = min(active_values.values())
            darkness_value = brightest_value

        # Smooth readings to prevent flickering
        self.light_history.append(darkness_value)

        self.light_average = (
            sum(self.light_history) /
            len(self.light_history)
        )

        # Higher darkness_value = darker
        if self.light_average >= LIGHT_DARK_THRESHOLD:
            self.low_light_count += 1
            self.good_light_count = 0

        elif self.light_average <= LIGHT_BRIGHT_THRESHOLD:
            self.good_light_count += 1
            self.low_light_count = 0

        else:
            self.low_light_count = 0
            self.good_light_count = 0

        if self.low_light_count >= STABLE_READINGS:
            self.light_low = True

        elif self.good_light_count >= STABLE_READINGS:
            self.light_low = False

        return active_values

    # ----------------------------------
    # COMBINED PLANT STATE
    # ----------------------------------

    def evaluate(self, data):

        self.evaluate_soil(data)
        self.evaluate_temperature(data)

        active_light = self.evaluate_light(data)

        plant_state = {
            "soil_dry": self.soil_dry is True,
            "temp_high": self.temp_high,
            "light_low": self.light_low,
            "searching_light": (
                SIMULATE_SEARCHING and self.light_low
            )
        }

        return plant_state, active_light


# ======================================
# MAIN PROGRAM
# ======================================

def main():

    controller = EmotionController()
    evaluator = PlantStateEvaluator()
    display = OLEDDisplay()

    current_emotion = None
    current_message = ""
    last_processed_version = -1
    plant_state = None

    sensor_thread = threading.Thread(
        target=read_sensors,
        daemon=True
    )
    sensor_thread.start()

    print("=" * 50)
    print("F03 - REAL SENSOR INTEGRATION")
    print("Soil + Temperature + Light")
    print("=" * 50)

    try:
        while display.running:

            with lock:
                data = (
                    latest_data.copy()
                    if latest_data else None
                )
                received_at = last_received
                error = serial_error
                version = data_version

            if error:
                emotion = "ERROR"
                message = "ESP32 connection error!"

            elif data is None:
                emotion = "LISTENING"
                message = "Waiting for sensor data..."

            elif time.monotonic() - received_at > SENSOR_TIMEOUT:
                emotion = "ERROR"
                message = "Sensor communication timeout!"

            else:

                # Process each sensor reading only once
                if version != last_processed_version:

                    plant_state, light_values = (
                        evaluator.evaluate(data)
                    )

                    last_processed_version = version

                    average = evaluator.light_average

                    if average is None:
                        light_text = "N/A"
                    else:
                        light_text = f"{average:.1f}"

                    print(
                        f"Soil: {data['soil_raw']} | "
                        f"Temp: {data.get('temperature', 'N/A')} | "
                        f"LDRs: {light_values} | "
                        f"Darkness: {light_text} | "
                        f"State: {plant_state}",
                        flush=True
                    )

                if evaluator.soil_dry is None:
                    emotion = "LISTENING"
                    message = "Checking soil moisture..."

                elif plant_state is not None:
                    emotion, message = (
                        controller.evaluate_state(
                            plant_state
                        )
                    )

                else:
                    emotion = "LISTENING"
                    message = "Checking sensors..."

            if emotion != current_emotion:

                print(
                    f"Emotion: "
                    f"{current_emotion} -> {emotion}",
                    flush=True
                )

                current_emotion = emotion

            if (
                emotion != display.current_emotion
                or message != current_message
            ):
                display.show_emotion(
                    emotion,
                    message
                )
                current_message = message

            if not display.update():
                break

    except KeyboardInterrupt:
        print("Stopping F03...")

    finally:
        stop_event.set()
        display.clear()
        display.close()


if __name__ == "__main__":
    main()
