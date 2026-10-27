
from datetime import datetime
from src.camera.camera_service import CameraService


class CameraScheduler:
    def __init__(self, capture_hour=12, capture_minute=0):
        self.camera_service = CameraService()
        self.capture_hour = capture_hour
        self.capture_minute = capture_minute

    def check_and_capture(self):
        now = datetime.now()

        scheduled_time = now.replace(
            hour=self.capture_hour,
            minute=self.capture_minute,
            second=0,
            microsecond=0
        )

        if now < scheduled_time:
            return None

        # Check if today's image already exists
        today = now.strftime("%Y-%m-%d")

        existing_images = list(
            self.camera_service.images_dir.glob(
                f"plant_{today}_*.jpg"
            )
        )

        if existing_images:
            return None

        return self.camera_service.capture_image()
