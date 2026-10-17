
import time

from src.sensors.light_tracker import LightTracker, LightReadings


class LightScheduler:
    def __init__(
        self,
        tracker: LightTracker,
        interval_minutes: float = 30,
        clock=None,
    ):
        if interval_minutes <= 0:
            raise ValueError("Interval must be positive")

        self.tracker = tracker
        self.interval_seconds = interval_minutes * 60
        self.clock = clock if clock is not None else time.monotonic
        self.next_check_time = None

    def check_if_due(
        self,
        readings: LightReadings,
        current_light: int,
    ):
        now = self.clock()

        if self.next_check_time is not None:
            if now < self.next_check_time:
                return None

        self.next_check_time = now + self.interval_seconds

        return self.tracker.evaluate(readings, current_light)
