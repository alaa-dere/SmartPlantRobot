
import cv2
import numpy as np
from pathlib import Path


class ImageAnalyzer:
    def analyze_image(self, image_path):
        image_path = Path(image_path)

        image = cv2.imread(str(image_path))

        if image is None:
            return {
                "status": "ERROR",
                "message": "Could not read image."
            }

        # Convert image from BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Approximate green and yellow color ranges
        green_lower = np.array([35, 40, 40])
        green_upper = np.array([85, 255, 255])

        yellow_lower = np.array([18, 40, 40])
        yellow_upper = np.array([34, 255, 255])

        green_mask = cv2.inRange(
            hsv, green_lower, green_upper
        )

        yellow_mask = cv2.inRange(
            hsv, yellow_lower, yellow_upper
        )

        green_pixels = cv2.countNonZero(green_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)

        total_pixels = green_pixels + yellow_pixels

        if total_pixels == 0:
            return {
                "status": "NO_PLANT_COLORS",
                "message": "No green or yellow regions detected."
            }

        yellow_percentage = (
            yellow_pixels / total_pixels
        ) * 100

        return {
            "status": "ANALYZED",
            "green_pixels": green_pixels,
            "yellow_pixels": yellow_pixels,
            "yellow_percentage": round(
                yellow_percentage, 2
            ),
            "message": "Color analysis completed."
        }
