
import json
from datetime import datetime
from pathlib import Path

from src.camera.image_analyzer import ImageAnalyzer
from src.camera.image_comparison import ImageComparisonService


class PlantHealthMonitor:
    def __init__(self):
        self.analyzer = ImageAnalyzer()
        self.comparison = ImageComparisonService()

        # Main data directory
        self.data_dir = (
            Path(__file__).resolve().parents[2] / "data"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File used to store analysis history
        self.history_file = (
            self.data_dir / "plant_health_history.json"
        )

    def process_image(self, image_path):
        # Step 1: Analyze the current image
        analysis = self.analyzer.analyze_image(image_path)

        if analysis["status"] != "ANALYZED":
            return analysis

        # Step 2: Load previous history
        history = []

        if self.history_file.exists():
            with open(
                self.history_file,
                "r",
                encoding="utf-8"
            ) as file:
                history = json.load(file)

        # Step 3: Find the previous image
        previous_image = (
            history[-1]["image_path"]
            if history else None
        )

        # Step 4: Compare images
        comparison = None

        if previous_image and Path(previous_image).exists():
            comparison = self.comparison.compare_images(
                previous_image,
                image_path
            )

        # Step 5: Create a new history record
        record = {
            "timestamp": datetime.now().isoformat(),
            "image_path": str(image_path),
            "analysis": analysis,
            "comparison": comparison
        }

        # Step 6: Save updated history
        history.append(record)

        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(history, file, indent=4)

        return record
