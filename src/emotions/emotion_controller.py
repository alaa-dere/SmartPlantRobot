class EmotionController:
    def __init__(self):
        self.EMOTIONS = {
            "HAPPY": "😊 Happy",
            "THIRSTY": "😢 Thirsty",
            "NEEDS_WATER": "😭 Needs Water",
            "HOT": "🥵 Hot",
            "NEEDS_LIGHT": "😕 Needs Light",
            "SEARCHING": "👀 Searching",
            "SLEEPING": "😴 Sleeping",
            "WAKE_UP": "😳 Wake Up",
            "LISTENING": "👂 Listening",
            "TALKING": "😄 Talking",
            "ERROR": "😵 Error"
        }

    def evaluate_state(self, sensor_data, ai_state="Idle", is_moving=False):
        if sensor_data.get("system_error", False):
            return self.EMOTIONS["ERROR"], "System hardware error!"
            
        if sensor_data.get("reservoir_empty", False):
            return self.EMOTIONS["NEEDS_WATER"], "Reservoir is empty, please fill water!"

        if ai_state == "Talking":
            return self.EMOTIONS["TALKING"], "AI is speaking..."
        if ai_state == "Listening":
            return self.EMOTIONS["LISTENING"], "AI is listening..."
        if sensor_data.get("pir_user_near", False):
            return self.EMOTIONS["WAKE_UP"], "User detected near the plant!"

        if sensor_data.get("soil_dry", False):
            return self.EMOTIONS["THIRSTY"], "Soil moisture is low!"
        if sensor_data.get("temp_high", False):
            return self.EMOTIONS["HOT"], "Temperature is too high!"
        if sensor_data.get("light_low", False):
            return self.EMOTIONS["NEEDS_LIGHT"], "Light level is insufficient!"

        if is_moving or sensor_data.get("searching_light", False):
            return self.EMOTIONS["SEARCHING"], "Plant is searching for light..."

        if sensor_data.get("is_sleeping", False):
            return self.EMOTIONS["SLEEPING"], "Plant is sleeping..."

        return self.EMOTIONS["HAPPY"], "Plant condition is healthy!"