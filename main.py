
import time

from src.camera.camera_scheduler import CameraScheduler
from src.camera.plant_health_monitor import PlantHealthMonitor


def main():
    print("Smart Plant Robot started!")

    camera_scheduler = CameraScheduler(
        capture_hour=12,
        capture_minute=0
    )

    health_monitor = PlantHealthMonitor()

    try:
        while True:
            # Capture one image per day
            image_path = camera_scheduler.check_and_capture()

            # Analyze only newly captured images
            if image_path is not None:
                print("Analyzing new plant image...")

                result = health_monitor.process_image(image_path)

                print("Analysis:", result.get("analysis"))
                print("Comparison:", result.get("comparison"))

            time.sleep(60)

    except KeyboardInterrupt:
        print("\nSmart Plant Robot stopped.")


if __name__ == "__main__":
    main()
