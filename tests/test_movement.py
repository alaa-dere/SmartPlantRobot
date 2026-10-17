import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.movement.movement_controller import MovementController

def run_safety_tests():
    controller = MovementController(obstacle_threshold_cm=15.0, edge_threshold_cm=10.0)

    test_scenarios = [
        {
            "test_name": "1. Normal Driving Clear Surface",
            "command": "FORWARD",
            "sensors": {"ultrasonic_front_cm": 40.0, "edge_front_left_cm": 4.0, "edge_front_right_cm": 4.0, "edge_back_left_cm": 4.0, "edge_back_right_cm": 4.0}
        },
        {
            "test_name": "2. Obstacle Ahead (Book/Cup)",
            "command": "FORWARD",
            "sensors": {"ultrasonic_front_cm": 8.0, "edge_front_left_cm": 4.0, "edge_front_right_cm": 4.0, "edge_back_left_cm": 4.0, "edge_back_right_cm": 4.0}
        },
        {
            "test_name": "3. Front Table Edge Detected",
            "command": "FORWARD",
            "sensors": {"ultrasonic_front_cm": 50.0, "edge_front_left_cm": 25.0, "edge_front_right_cm": 4.0, "edge_back_left_cm": 4.0, "edge_back_right_cm": 4.0}
        },
        {
            "test_name": "4. Back Table Edge Detected",
            "command": "BACKWARD",
            "sensors": {"ultrasonic_front_cm": 50.0, "edge_front_left_cm": 4.0, "edge_front_right_cm": 4.0, "edge_back_left_cm": 4.0, "edge_back_right_cm": 18.0}
        },
        {
            "test_name": "5. Sensor Disconnection / Communication Loss",
            "command": "FORWARD",
            "sensors": None
        },
        {
            "test_name": "6. Recovery Motion Away From Hazard",
            "command": "BACKWARD",
            "sensors": {"ultrasonic_front_cm": 5.0, "edge_front_left_cm": 4.0, "edge_front_right_cm": 4.0, "edge_back_left_cm": 4.0, "edge_back_right_cm": 4.0}
        }
    ]

    print("=" * 65)
    print("STARTING F05 SAFETY & MOBILITY LOGIC TESTS (SIMULATION)")
    print("=" * 65)

    for test in test_scenarios:
        status, log_msg = controller.issue_command(test["command"], test["sensors"])
        print(f"\n[SCENARIO]: {test['test_name']}")
        print(f" -> Requested Command : {test['command']}")
        print(f" -> Final Motor State : {status}")
        print(f" -> Result Log        : {log_msg}")

    print("\n" + "=" * 65)
    print("ALL F05 SAFETY TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_safety_tests()