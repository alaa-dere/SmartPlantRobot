
import subprocess
from pathlib import Path

from leafy_chat_v2 import (
    read_sensors,
    validate_sensors,
    interpret_state,
    plant_response,
    ask_ai
)

AUDIO_FILE = Path.home() / "SmartPlantRobot" / "leafy_reply.wav"

print("=== LEAFY AI VOICE TEST ===")
print("Offline AI + Real Sensors + Speech")
print("Type 'exit' to quit.\n")

history = []

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    print("Reading sensors...")
    frames = read_sensors()
    readings, error = validate_sensors(frames)
    state = interpret_state(readings, error)

    answer = plant_response(question, state)

    if answer is None:
        print("Leafy is thinking...")
        answer = ask_ai(question, state, history)

    print("Leafy:", answer)

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    history = history[-6:]

    subprocess.run([
        "espeak-ng",
        "-v", "en-us+f3",
        "-s", "145",
        "-w", str(AUDIO_FILE),
        answer
    ], check=True)

    print("Audio saved:", AUDIO_FILE)

    # Enable playback only with a safe audio device.
    # This currently plays through Raspberry Pi's HDMI audio.
    # If HDMI has no speakers, the WAV file is still saved.
    print("Voice generated successfully!\n")
