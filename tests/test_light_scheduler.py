
import unittest

from src.sensors.light_tracker import LightTracker, LightReadings
from src.sensors.light_scheduler import LightScheduler


class FakeClock:
    def __init__(self):
        self.current_time = 0

    def __call__(self):
        return self.current_time

    def advance(self, seconds):
        self.current_time += seconds


class TestLightScheduler(unittest.TestCase):

    def setUp(self):
        self.clock = FakeClock()
        self.tracker = LightTracker(
            min_light=700,
            tolerance=100
        )
        self.scheduler = LightScheduler(
            tracker=self.tracker,
            interval_minutes=30,
            clock=self.clock
        )

        self.readings = LightReadings(
            front=1200,
            back=300,
            left=500,
            right=400
        )

    def test_first_check_runs_immediately(self):
        result = self.scheduler.check_if_due(
            self.readings, current_light=400
        )
        self.assertEqual(result, "FRONT")

    def test_no_check_before_30_minutes(self):
        self.scheduler.check_if_due(
            self.readings, current_light=400
        )

        self.clock.advance(1799)

        result = self.scheduler.check_if_due(
            self.readings, current_light=400
        )
        self.assertIsNone(result)

    def test_check_after_30_minutes(self):
        self.scheduler.check_if_due(
            self.readings, current_light=400
        )

        self.clock.advance(1800)

        result = self.scheduler.check_if_due(
            self.readings, current_light=400
        )
        self.assertEqual(result, "FRONT")

    def test_stay_when_light_is_sufficient(self):
        result = self.scheduler.check_if_due(
            self.readings, current_light=900
        )
        self.assertEqual(result, "STAY")

    def test_low_light_in_all_directions(self):
        readings = LightReadings(
            front=200,
            back=100,
            left=300,
            right=150
        )

        result = self.scheduler.check_if_due(
            readings, current_light=200
        )
        self.assertEqual(result, "LOW_LIGHT")


if __name__ == "__main__":
    unittest.main()
