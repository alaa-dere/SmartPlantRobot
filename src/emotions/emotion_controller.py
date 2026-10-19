
class EmotionController:
    def __init__(self):
        self.EMOTIONS = {
            "HAPPY": "Happy",
            "THIRSTY": "Thirsty",
            "NEEDS_WATER": "Needs Water",
            "HOT": "Hot",
            "NEEDS_LIGHT": "Needs Light",
            "SEARCHING": "Searching",
            "SLEEPING": "Sleeping",
            "WAKE_UP": "Wake Up",
            "LISTENING": "Listening",
            "TALKING": "Talking",
            "ERROR": "Error"
        }

    def evaluate_state(
        self,
        sensor_data,
        ai_state="Idle",
        is_moving=False
    ):
        if sensor_data.get("system_error", False):
            return "ERROR", "System hardware error!"

        if sensor_data.get("reservoir_empty", False):
            return "NEEDS_WATER", "Please fill the water tank!"

        if sensor_data.get("soil_dry", False):
            return "THIRSTY", "I need some water!"

        if sensor_data.get("temp_high", False):
            return "HOT", "It is too hot!"

        if ai_state == "Talking":
            return "TALKING", "I am talking!"

        if ai_state == "Listening":
            return "LISTENING", "I am listening!"

        if sensor_data.get("pir_user_near", False):
            return "WAKE_UP", "Hello there!"

        # Active light searching comes before low light
        if is_moving or sensor_data.get(
            "searching_light", False
        ):
            return "SEARCHING", "Looking for sunlight!"

        if sensor_data.get("light_low", False):
            return "NEEDS_LIGHT", "I need more sunlight!"

        if sensor_data.get("is_sleeping", False):
            return "SLEEPING", "Zzz..."

        return "HAPPY", "I am happy and healthy!"
