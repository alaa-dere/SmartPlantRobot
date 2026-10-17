
import unittest

from src.sensors.light_tracker import LightReadings, LightTracker


class TestLightTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = LightTracker(min_light=500, tolerance=100)

    def test_front_has_strongest_light(self):
        readings = LightReadings(2500, 800, 1200, 1800)
        self.assertEqual(
            self.tracker.get_best_direction(readings), "FRONT"
        )

    def test_left_has_strongest_light(self):
        readings = LightReadings(1200, 800, 3000, 1800)
        self.assertEqual(
            self.tracker.get_best_direction(readings), "LEFT"
        )

    def test_low_light(self):
        readings = LightReadings(200, 100, 150, 180)
        self.assertEqual(
            self.tracker.get_best_direction(readings), "LOW_LIGHT"
        )

    def test_balanced_light(self):
        readings = LightReadings(1500, 1450, 1480, 1520)
        self.assertEqual(
            self.tracker.get_best_direction(readings), "BALANCED"
        )


if __name__ == "__main__":
    unittest.main()
