
from src.camera.image_analyzer import ImageAnalyzer


class ImageComparisonService:
    def __init__(self):
        self.analyzer = ImageAnalyzer()

    def compare_images(self, previous_image, current_image):
        previous = self.analyzer.analyze_image(previous_image)
        current = self.analyzer.analyze_image(current_image)

        if (
            previous["status"] != "ANALYZED"
            or current["status"] != "ANALYZED"
        ):
            return {
                "status": "ERROR",
                "message": "One or both images could not be analyzed."
            }

        previous_yellow = previous["yellow_percentage"]
        current_yellow = current["yellow_percentage"]

        difference = round(
            current_yellow - previous_yellow, 2
        )

        if difference > 0:
            message = "Yellow regions increased."
        elif difference < 0:
            message = "Yellow regions decreased."
        else:
            message = "No change in yellow regions."

        return {
            "status": "COMPARED",
            "previous_yellow_percentage": previous_yellow,
            "current_yellow_percentage": current_yellow,
            "difference_percentage_points": difference,
            "message": message
        }
