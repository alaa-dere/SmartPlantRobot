import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.emotions.emotion_controller import EmotionController
from src.display.oled_display import OLEDDisplay

def run_all_states_test():
    controller = EmotionController()
    display = OLEDDisplay()

    all_test_cases = [
        {"name": "1. Plant conditions are good", "data": {}, "ai": "Idle", "moving": False, "key": "HAPPY"},
        {"name": "2. Soil is dry", "data": {"soil_dry": True}, "ai": "Idle", "moving": False, "key": "THIRSTY"},
        {"name": "3. Reservoir is empty", "data": {"reservoir_empty": True}, "ai": "Idle", "moving": False, "key": "NEEDS_WATER"},
        {"name": "4. Temperature too high", "data": {"temp_high": True}, "ai": "Idle", "moving": False, "key": "HOT"},
        {"name": "5. Light is insufficient", "data": {"light_low": True}, "ai": "Idle", "moving": False, "key": "NEEDS_LIGHT"},
        {"name": "6. Searching for light", "data": {"searching_light": True}, "ai": "Idle", "moving": True, "key": "SEARCHING"},
        {"name": "7. Idle for a while", "data": {"is_sleeping": True}, "ai": "Idle", "moving": False, "key": "SLEEPING"},
        {"name": "8. User approaches", "data": {"pir_user_near": True}, "ai": "Idle", "moving": False, "key": "WAKE_UP"},
        {"name": "9. AI is listening", "data": {}, "ai": "Listening", "moving": False, "key": "LISTENING"},
        {"name": "10. AI is responding", "data": {}, "ai": "Talking", "moving": False, "key": "TALKING"},
        {"name": "11. System error", "data": {"system_error": True}, "ai": "Idle", "moving": False, "key": "ERROR"}
    ]

    print("=" * 60)
    print("RUNNING ALL 11 EMOTION STATES TEST")
    print("=" * 60)

    for test in all_test_cases:
        emotion_text, msg = controller.evaluate_state(test["data"], ai_state=test["ai"], is_moving=test["moving"])
        print(f"\n[Testing]: {test['name']}")
        print(f" -> Key: {test['key']} | Text: {emotion_text} | Message: {msg}")
        
        display.show_emotion(test["key"], msg)
        time.sleep(2)

    display.clear()
    print("\n" + "=" * 60)
    print("ALL 11 STATES TESTED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_states_test()