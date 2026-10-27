
import cv2
from datetime import datetime
from pathlib import Path


class CameraService:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

        self.images_dir = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "plant_images"
        )

        self.images_dir.mkdir(parents=True, exist_ok=True)

    def capture_image(self):
        camera = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_V4L2
        )

        if not camera.isOpened():
            camera.release()
            print("ERROR: Camera could not be opened.")
            return None

        try:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            frame = None

            # Allow camera exposure to stabilize
            for _ in range(10):
                success, image = camera.read()

                if success and image is not None:
                    frame = image

            if frame is None:
                print("ERROR: Failed to capture image.")
                return None

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S_%f"
            )

            image_path = (
                self.images_dir / f"plant_{timestamp}.jpg"
            )

            if not cv2.imwrite(str(image_path), frame):
                print("ERROR: Failed to save image.")
                return None

            print(f"SUCCESS: Image saved to {image_path}")
            return str(image_path)

        except cv2.error as error:
            print(f"Camera error: {error}")
            return None

        finally:
            camera.release()
