
import json
from datetime import datetime
from pathlib import Path

from src.camera.image_analyzer import ImageAnalyzer
from src.camera.image_comparison import ImageComparisonService


class PlantHealthMonitor:
    def __init__(self):
        self.analyzer = ImageAnalyzer()
        self.comparison = ImageComparisonService()

        self.data_dir = Path(__file__).resolve().parents[2] / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.data_dir / "plant_health_history.json"

    def process_image(self, image_path):
        analysis = self.analyzer.analyze_image(image_path)

        if analysis["status"] != "ANALYZED":
            return analysis

        history = []

        if self.history_file.exists():
            with open(self.history_file, "r") as file:
                history = json.load(file)

        previous_image = history[-1]["image_path"] if history else None
        comparison = None

        if previous_image and Path(previous_image).exists():
            comparison = self.comparison.compare_images(
                previous_image, image_path
            )

        record = {
            "timestamp": datetime.now().isoformat(),
            "image_path": str(image_path),
            "analysis": analysis,
            "comparison": comparison
        }

        history.append(record)

        with open(self.history_file, "w") as file:
            json.dump(history, file, indent=4)

        return record
