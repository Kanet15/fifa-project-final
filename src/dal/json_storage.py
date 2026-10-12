import json
import os
from typing import List, Dict, Any

class JSONStorageManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.pets_file = os.path.join(data_dir, "pets.json")
        self.apps_file = os.path.join(data_dir, "applications.json")
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.pets_file):
            with open(self.pets_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.apps_file):
            with open(self.apps_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def load_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.pets_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.pets_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_applications(self) -> List[Dict[str, Any]]:
        try:
            with open(self.apps_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_applications(self, data: List[Dict[str, Any]]) -> None:
        with open(self.apps_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)