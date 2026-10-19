
import time
import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from src.emotions.emotion_controller import EmotionController
from src.display.oled_display import OLEDDisplay


def run_all_states_test():
    controller = EmotionController()
    display = OLEDDisplay()

    all_test_cases = [
        {
            "name": "Happy",
            "data": {},
            "ai": "Idle",
            "moving": False,
            "key": "HAPPY"
        },
        {
            "name": "Thirsty",
            "data": {"soil_dry": True},
            "ai": "Idle",
            "moving": False,
            "key": "THIRSTY"
        },
        {
            "name": "Needs Water",
            "data": {"reservoir_empty": True},
            "ai": "Idle",
            "moving": False,
            "key": "NEEDS_WATER"
        },
        {
            "name": "Hot",
            "data": {"temp_high": True},
            "ai": "Idle",
            "moving": False,
            "key": "HOT"
        },
        {
            "name": "Needs Light",
            "data": {"light_low": True},
            "ai": "Idle",
            "moving": False,
            "key": "NEEDS_LIGHT"
        },
        {
            "name": "Searching",
            "data": {"searching_light": True},
            "ai": "Idle",
            "moving": True,
            "key": "SEARCHING"
        },
        {
            "name": "Sleeping",
            "data": {"is_sleeping": True},
            "ai": "Idle",
            "moving": False,
            "key": "SLEEPING"
        },
        {
            "name": "Wake Up",
            "data": {"pir_user_near": True},
            "ai": "Idle",
            "moving": False,
            "key": "WAKE_UP"
        },
        {
            "name": "Listening",
            "data": {},
            "ai": "Listening",
            "moving": False,
            "key": "LISTENING"
        },
        {
            "name": "Talking",
            "data": {},
            "ai": "Talking",
            "moving": False,
            "key": "TALKING"
        },
        {
            "name": "Error",
            "data": {"system_error": True},
            "ai": "Idle",
            "moving": False,
            "key": "ERROR"
        }
    ]

    print("=" * 60)
    print("F03 - FACE & EMOTIONAL STATE TEST")
    print("=" * 60)

    completed = 0

    try:
        for test in all_test_cases:
            emotion_key, message = controller.evaluate_state(
                test["data"],
                ai_state=test["ai"],
                is_moving=test["moving"]
            )

            print(f"\nTesting: {test['name']}")
            print(f"Emotion: {emotion_key}")
            print(f"Message: {message}")

            if emotion_key != test["key"]:
                print("FAILED: Wrong emotion!")
                break

            display.show_emotion(emotion_key, message)

            start = time.monotonic()

            while time.monotonic() - start < 3:
                if not display.update():
                    print("Test stopped by user.")
                    return

            completed += 1
            print("PASSED")

        if completed == len(all_test_cases):
            print("\nALL 11 EMOTION STATES PASSED!")
        else:
            print(f"\nCompleted {completed} of 11 states.")

    finally:
        display.clear()
        display.close()


if __name__ == "__main__":
    run_all_states_test()
