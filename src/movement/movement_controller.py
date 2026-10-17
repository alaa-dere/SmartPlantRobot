import time

class MovementController:
    def __init__(self, obstacle_threshold_cm=15.0, edge_threshold_cm=10.0):
        self.OBSTACLE_THRESHOLD_CM = obstacle_threshold_cm
        self.EDGE_THRESHOLD_CM = edge_threshold_cm
        self.current_state = "STOP"
        self.is_hardware_active = False

    def evaluate_safety(self, sensor_data):
        if not sensor_data or not isinstance(sensor_data, dict):
            return False, "FAIL-SAFE: Invalid or disconnected sensor data!"

        front_obstacle = sensor_data.get("ultrasonic_front_cm", 999.0)
        if front_obstacle <= self.OBSTACLE_THRESHOLD_CM:
            return False, f"OBSTACLE DETECTED: {front_obstacle}cm ahead!"

        edge_front_left = sensor_data.get("edge_front_left_cm", 0.0)
        edge_front_right = sensor_data.get("edge_front_right_cm", 0.0)
        edge_back_left = sensor_data.get("edge_back_left_cm", 0.0)
        edge_back_right = sensor_data.get("edge_back_right_cm", 0.0)

        if edge_front_left > self.EDGE_THRESHOLD_CM or edge_front_right > self.EDGE_THRESHOLD_CM:
            return False, "FRONT EDGE DETECTED: Missing table surface at front!"

        if edge_back_left > self.EDGE_THRESHOLD_CM or edge_back_right > self.EDGE_THRESHOLD_CM:
            return False, "BACK EDGE DETECTED: Missing table surface at back!"

        return True, "SAFE"

    def issue_command(self, requested_command, sensor_data):
        is_safe, reason = self.evaluate_safety(sensor_data)

        if not is_safe:
            if requested_command == "BACKWARD" and "FRONT" in reason:
                edge_bl = sensor_data.get("edge_back_left_cm", 0.0)
                edge_br = sensor_data.get("edge_back_right_cm", 0.0)
                if edge_bl <= self.EDGE_THRESHOLD_CM and edge_br <= self.EDGE_THRESHOLD_CM:
                    self.current_state = "BACKWARD"
                    return self.current_state, f"RECOVERY MOVE: Executing BACKWARD away from front danger."

            self.current_state = "STOP"
            return "STOP", f"EMERGENCY STOP ACTIVATED -> {reason}"

        if requested_command in ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"]:
            self.current_state = requested_command
            return self.current_state, f"Command '{requested_command}' executed safely."
        else:
            self.current_state = "STOP"
            return "STOP", "Unknown command! Stopping for safety."