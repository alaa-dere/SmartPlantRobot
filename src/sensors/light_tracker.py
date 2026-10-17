
from dataclasses import dataclass


@dataclass
class LightReadings:
    front: int
    back: int
    left: int
    right: int


class LightTracker:
    def __init__(self, min_light=700, tolerance=100):
        self.min_light = min_light
        self.tolerance = tolerance

    def get_best_direction(self, readings: LightReadings) -> str:
        values = {
            "FRONT": readings.front,
            "BACK": readings.back,
            "LEFT": readings.left,
            "RIGHT": readings.right,
        }

        best_direction = max(values, key=values.get)
        best_value = values[best_direction]

        if best_value < self.min_light:
            return "LOW_LIGHT"

        if best_value - min(values.values()) <= self.tolerance:
            return "BALANCED"

        return best_direction

    def should_move(self, current_light: int) -> bool:
        return current_light < self.min_light

    def evaluate(
        self, readings: LightReadings, current_light: int
    ) -> str:
        if not self.should_move(current_light):
            return "STAY"

        return self.get_best_direction(readings)
