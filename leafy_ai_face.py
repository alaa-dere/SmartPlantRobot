
import os
import time
import queue
import threading

# Existing project modules
from src.display.oled_display import OLEDDisplay
from src.emotions.emotion_controller import EmotionController

from leafy_chat_v2 import (
    read_sensors,
    validate_sensors,
    interpret_state,
    memory_response,
    plant_response,
    ask_ai
)

# =====================================
# CONFIGURATION
# =====================================

MAX_HISTORY = 6
TALKING_DISPLAY_SECONDS = 3

requests = queue.Queue()
events = queue.Queue()
stop_event = threading.Event()


# =====================================
# INPUT THREAD
# =====================================

def input_worker():
    while not stop_event.is_set():
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            question = "exit"

        if question.lower() in ("exit", "quit", "bye"):
            events.put(("exit", None))
            break

        if question:
            requests.put(question)


# =====================================
# AI WORKER
# =====================================

def ai_worker():
    history = []

    while not stop_event.is_set():
        try:
            question = requests.get(timeout=0.2)
        except queue.Empty:
            continue

        # First try conversation memory
        answer = memory_response(question, history)
        state = None

        if answer is not None:
            source = "Conversation Memory"

        else:
            events.put(("thinking", None))

            frames = read_sensors()
            readings, error = validate_sensors(frames)
            state = interpret_state(readings, error)

            print("\nCurrent state:", state)

            answer = plant_response(question, state)

            if answer is not None:
                source = "Plant State Interpreter"
            else:
                source = "Local AI"
                answer = ask_ai(
                    question, state, history
                )

        history.append({
            "role": "user",
            "content": question
        })
        history.append({
            "role": "assistant",
            "content": answer
        })
        history = history[-MAX_HISTORY:]

        events.put((
            "answer",
            {
                "text": answer,
                "state": state,
                "source": source
            }
        ))

        requests.task_done()


# =====================================
# DISPLAY STATE
# =====================================

def get_plant_emotion(state, controller):
    if state is None:
        return "HAPPY", "Hello, my friend!"

    if state.get("warning"):
        return "ERROR", "Sensor data needs checking"

    soil = state.get("soil")

    if soil == "UNAVAILABLE":
        return "ERROR", "Soil data unavailable"

    sensor_flags = {
        "soil_dry": soil == "POSSIBLY_DRY",
        "system_error": False,
        "reservoir_empty": False,
        "temp_high": False,
        "light_low": False,
        "searching_light": False,
        "is_sleeping": False
    }

    if soil == "POSSIBLY_DRY":
        # Preliminary interpretation only
        return "THIRSTY", "My soil might be dry"

    if soil == "UNCERTAIN":
        return "HAPPY", "Checking my soil"

    if soil == "POSSIBLY_MOIST":
        return "HAPPY", "My soil seems moist"

    return controller.evaluate_state(sensor_flags)


# =====================================
# MAIN
# =====================================

def main():
    display = OLEDDisplay()
    controller = EmotionController()

    current_state = None
    previous_emotion = "HAPPY"
    previous_message = "Hello! I am Leafy!"

    talking_until = 0
    running = True

    input_thread = threading.Thread(
        target=input_worker,
        daemon=True
    )

    ai_thread = threading.Thread(
        target=ai_worker,
        daemon=True
    )

    input_thread.start()
    ai_thread.start()

    print("=" * 45)
    print("LEAFY AI + FACE INTEGRATION")
    print("=" * 45)
    print("Type a question in English.")
    print("Type 'exit' to quit.\n")

    display.show_emotion(
        previous_emotion,
        previous_message
    )

    try:
        while running and display.running:

            # Process events from workers
            try:
                event, data = events.get_nowait()
            except queue.Empty:
                event = None
                data = None

            if event == "exit":
                running = False

            elif event == "thinking":
                previous_emotion = "SEARCHING"
                previous_message = "Thinking..."

                display.show_emotion(
                    previous_emotion,
                    previous_message
                )

            elif event == "answer":
                answer = data["text"]
                source = data["source"]

                if data["state"] is not None:
                    current_state = data["state"]

                print("\nSource:", source)
                print("Leafy:", answer, "\n")

                previous_emotion = "TALKING"
                previous_message = answer

                talking_until = (
                    time.monotonic()
                    + TALKING_DISPLAY_SECONDS
                )

                display.show_emotion(
                    "TALKING",
                    answer
                )

            # Return face to plant condition
            if (
                talking_until > 0
                and time.monotonic() >= talking_until
            ):
                talking_until = 0

                emotion, message = get_plant_emotion(
                    current_state,
                    controller
                )

                previous_emotion = emotion
                previous_message = message

                display.show_emotion(
                    emotion,
                    message
                )

            # Keep pygame responsive
            if not display.update():
                running = False

    except KeyboardInterrupt:
        print("\nStopping Leafy...")

    finally:
        stop_event.set()
        display.close()
        print("Leafy stopped.")


if __name__ == "__main__":
    main()
