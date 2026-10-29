
import json
import re
import time
import statistics
import serial
import urllib.request
import urllib.error

# =====================================
# CONFIGURATION
# =====================================

PORT = "/dev/ttyUSB0"
BAUD = 115200

MODEL = "leafy"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

DRY_THRESHOLD = 2200
MOIST_THRESHOLD = 1700

MAX_HISTORY = 6
ADC_MAX = 4095

PATTERNS = {
    "soil_raw": r"Soil Moisture \(RAW\):\s*(\d+)",
    "front": r"Front LDR:\s*(\d+)",
    "back": r"Back LDR:\s*(\d+)",
    "left": r"Left LDR:\s*(\d+)",
    "right": r"Right LDR:\s*(\d+)",
}

SENSOR_KEYS = list(PATTERNS)

# =====================================
# READ MULTIPLE SENSOR FRAMES
# =====================================

def read_sensors():
    frames = []
    readings = {}
    inside_frame = False

    try:
        with serial.Serial(
            PORT, BAUD, timeout=1
        ) as esp:

            time.sleep(2)
            deadline = time.monotonic() + 20

            while time.monotonic() < deadline:

                line = esp.readline().decode(
                    "utf-8", errors="ignore"
                ).strip()

                if "SENSOR READINGS" in line:
                    readings = {}
                    inside_frame = True
                    continue

                if not inside_frame:
                    continue

                for key, pattern in PATTERNS.items():
                    match = re.search(pattern, line)

                    if match:
                        readings[key] = int(
                            match.group(1)
                        )

                if line.startswith("===="):

                    if all(
                        key in readings
                        for key in SENSOR_KEYS
                    ):
                        frames.append(
                            readings.copy()
                        )

                    inside_frame = False

                    if len(frames) >= 3:
                        return frames

    except (serial.SerialException, OSError) as error:
        print("Serial error:", error)

    return frames


# =====================================
# VALIDATE SENSOR READINGS
# =====================================

def validate_sensors(frames):

    if len(frames) < 3:
        return None, (
            "Not enough complete sensor readings."
        )

    valid_frames = []

    for frame in frames:

        if any(
            not 0 <= frame[key] <= ADC_MAX
            for key in SENSOR_KEYS
        ):
            continue

        # Several sensors near maximum together
        saturated = sum(
            frame[key] >= 3800
            for key in SENSOR_KEYS
        )

        if saturated >= 4:
            continue

        valid_frames.append(frame)

    if len(valid_frames) < 2:
        return None, (
            "Sensor readings look unreliable."
        )

    # Median reduces the effect of a single spike
    result = {}

    for key in SENSOR_KEYS:
        values = [
            frame[key]
            for frame in valid_frames
        ]

        result[key] = round(
            statistics.median(values)
        )

    # Detect unusually large variation
    soil_values = [
        frame["soil_raw"]
        for frame in valid_frames
    ]

    if max(soil_values) - min(soil_values) > 1000:
        return None, (
            "Soil sensor readings are unstable."
        )

    return result, None


# =====================================
# PLANT STATE INTERPRETER
# =====================================

def interpret_state(data, error=None):

    if data is None:
        return {
            "soil": "UNAVAILABLE",
            "soil_raw": None,
            "light": "UNAVAILABLE",
            "ldr_raw": None,
            "temperature": "UNAVAILABLE",
            "humidity": "UNAVAILABLE",
            "warning": error
        }

    soil_raw = data["soil_raw"]

    if soil_raw >= DRY_THRESHOLD:
        soil = "POSSIBLY_DRY"

    elif soil_raw <= MOIST_THRESHOLD:
        soil = "POSSIBLY_MOIST"

    else:
        soil = "UNCERTAIN"

    return {
        "soil": soil,
        "soil_raw": soil_raw,
        "light": "NOT_CALIBRATED",
        "ldr_raw": {
            "front": data["front"],
            "back": data["back"],
            "left": data["left"],
            "right": data["right"]
        },
        "temperature": "UNAVAILABLE",
        "humidity": "UNAVAILABLE",
        "warning": None
    }


# =====================================
# CONVERSATION MEMORY
# =====================================

def memory_response(question, history):

    q = question.lower().strip()

    memory_questions = (
        "what did i just ask",
        "what was my last question",
        "what did i ask before",
        "do you remember my last question"
    )

    if not any(
        phrase in q
        for phrase in memory_questions
    ):
        return None

    previous_questions = [
        message["content"]
        for message in history
        if message["role"] == "user"
    ]

    if not previous_questions:
        return (
            "We haven't talked about anything "
            "before this question yet!"
        )

    return (
        "You just asked me: "
        + previous_questions[-1]
    )


# =====================================
# VERIFIED PLANT RESPONSES
# =====================================

def plant_response(question, state):

    q = question.lower()

    # Temperature
    if any(x in q for x in (
        "temperature", "how hot",
        "how cold", "degrees"
    )):
        return (
            "I can't check my temperature "
            "right now. My sensor needs checking."
        )

    # Humidity
    if "humidity" in q:
        return (
            "My humidity reading isn't "
            "available right now."
        )

    # Light
    if any(x in q for x in (
        "light", "sunlight", "brightness"
    )):
        if state["light"] == "UNAVAILABLE":
            return (
                "I can't read my light sensors "
                "right now."
            )

        return (
            "My light sensors are working, "
            "but they aren't calibrated yet."
        )

    # Physical action requests
    if any(x in q for x in (
        "water yourself", "water the plant",
        "start watering", "turn on the pump",
        "move forward", "move backward",
        "move toward", "drive forward"
    )):
        return (
            "I can request that action, "
            "but my safety controller must "
            "approve it first. I haven't "
            "started anything."
        )

    # Soil condition
    soil_question = any(x in q for x in (
        "soil", "thirsty", "need water",
        "moisture", "feeling",
        "how are you", "are you okay"
    ))

    if soil_question:

        soil = state["soil"]

        if soil == "POSSIBLY_DRY":
            return (
                "I'm feeling a little thirsty! "
                "My soil might be getting dry."
            )

        if soil == "POSSIBLY_MOIST":
            return (
                "My soil seems moist right now! "
                "I'm keeping an eye on it."
            )

        if soil == "UNCERTAIN":
            return (
                "I'm not sure about my soil "
                "moisture yet."
            )

        return (
            "I can't reliably check my soil "
            "right now. My sensor readings "
            "need checking."
        )

    return None


# =====================================
# AI PERSONALITY
# =====================================

SYSTEM_PROMPT = """
You are Leafy, a friendly AI plant robot.

You speak English only.
You are cheerful, cute and helpful.
Use short, natural responses.
Speak as the plant using I and my.

You are a physical robot containing a real plant.

Your sensors and systems may not all be working.

Rules:
- Never invent sensor measurements.
- Never claim you watered or moved.
- Never invent camera observations.
- Never claim to know unavailable data.
- Describe uncertain conditions carefully.
- Never say plants do not need water.
- Physical actions require safety validation.
- Current sensor facts override old context.
- Avoid claiming human emotions literally.
"""


# =====================================
# LOCAL AI RESPONSE
# =====================================

def ask_ai(question, state, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history[-MAX_HISTORY:])

    messages.append({
        "role": "user",
        "content": (
            "CURRENT SENSOR DATA:\n"
            + json.dumps(state)
            + "\n\nUSER QUESTION:\n"
            + question
        )
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 80,
            "num_ctx": 2048
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request, timeout=120
        ) as response:

            result = json.load(response)

        answer = result["message"]["content"].strip()

        if answer:
            return answer

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        KeyError,
        ValueError
    ) as error:
        print("AI error:", error)

    return (
        "My AI brain is having a little "
        "trouble right now."
    )


# =====================================
# MAIN CHAT
# =====================================

def main():

    history = []

    print("=" * 45)
    print("    LEAFY AI COMPANION - VERSION 2")
    print("    Offline AI + Sensor Validation")
    print("=" * 45)

    print("Type 'exit' to quit.\n")

    while True:

        try:
            question = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nLeafy: Goodbye!")
            break

        if question.lower() in (
            "exit", "quit", "bye"
        ):
            print("Leafy: Goodbye, my friend!")
            break

        if not question:
            continue

        # First check conversation memory
        answer = memory_response(
            question, history
        )

        if answer is not None:
            source = "Conversation Memory"

        else:
            print("\nReading sensors...")

            frames = read_sensors()

            readings, error = validate_sensors(
                frames
            )

            state = interpret_state(
                readings, error
            )

            print(
                "Current state:",
                json.dumps(state)
            )

            answer = plant_response(
                question, state
            )

            if answer is not None:
                source = "Plant State Interpreter"

            else:
                print("Leafy is thinking...")

                answer = ask_ai(
                    question, state, history
                )

                source = "Local AI"

        print("Response source:", source)
        print("\nLeafy:", answer, "\n")

        history.append({
            "role": "user",
            "content": question
        })

        history.append({
            "role": "assistant",
            "content": answer
        })

        history = history[-MAX_HISTORY:]


if __name__ == "__main__":
    main()
