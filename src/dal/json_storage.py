import json
import os

class JSONStorageManager:
    """Data Access Layer (DAL)"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def read_json(self, filename="pets.json"):
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return []

    def write_json(self, filename="pets.json", data=None):
        if isinstance(filename, (list, dict)) and data is None:
            data = filename
            filename = "pets.json"

        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data if data is not None else [], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False

    # Aliases สำหรับทุกชื่อฟังก์ชัน
    def load_applications(self, filename="applications.json"): return self.read_json(filename)
    def save_applications(self, data, filename="applications.json"): return self.write_json(filename, data)
    def load_pets(self, filename="pets.json"): return self.read_json(filename)
    def save_pets(self, data, filename="pets.json"): return self.write_json(filename, data)
    def load_data(self, filename="pets.json"): return self.read_json(filename)
    def save_data(self, data, filename="pets.json"): return self.write_json(filename, data)

    load_json = read_json
    save_json = write_json
    get_data = read_json

# Alias รองรับชื่อคลาสแบบเดิม
JSONStorage = JSONStorageManager