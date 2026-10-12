import json
import os
import sys

# เพิ่ม Path ป้องกันปัญหา Import
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

for p in [project_root, src_dir, current_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Safe import JSONStorageManager
try:
    from src.dal.json_storage import JSONStorageManager
except Exception:
    try:
        from dal.json_storage import JSONStorageManager
    except Exception:
        try:
            from json_storage import JSONStorageManager
        except Exception:
            class JSONStorageManager:
                def __init__(self, data_dir="data"): self.data_dir = data_dir
                def read_json(self, f="pets.json"): return []
                def write_json(self, f="pets.json", d=None): return True

# Safe import PetfinderAPIService
try:
    from src.api_service import PetfinderAPIService
except Exception:
    try:
        from api_service import PetfinderAPIService
    except Exception:
        class PetfinderAPIService:
            def fetch_pets_from_api(self, pet_type=None): return None

# Smart Wrapper: ทำให้ dict รองรับทั้ง p.pet_id, p.id และ p['id']
class PetObj(dict):
    def __getattr__(self, item):
        if item == "pet_id":
            return self.get("pet_id", self.get("id"))
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

class PetService:
    def __init__(self, storage=None):
        if storage is not None:
            self.storage = storage
        else:
            self.storage = JSONStorageManager()
        self.api_service = PetfinderAPIService()

    def _wrap_pets(self, raw_pets):
        if not raw_pets:
            return []
        wrapped = []
        for p in raw_pets:
            if isinstance(p, dict):
                wrapped.append(PetObj(p))
            else:
                wrapped.append(p)
        return wrapped

    def get_all_pets(self):
        pets = self.storage.read_json("pets.json")
        if not pets and hasattr(self.storage, 'load_pets'):
            pets = self.storage.load_pets()
        return self._wrap_pets(pets)

    def get_filtered_pets(self, pet_type="All", search_query="", age="All", gender="All"):
        api_pets = self.api_service.fetch_pets_from_api(pet_type=pet_type)
        if api_pets is not None and len(api_pets) > 0:
            pets = api_pets
            using_api = True
        else:
            pets = self.get_all_pets()
            using_api = False

        query = search_query.strip().lower() if search_query else ""
        filtered = []

        for pet in pets:
            p_name = str(pet.get('name', '')).lower()
            breed_data = pet.get('breed', '')
            p_breed = breed_data.get('primary', '') if isinstance(breed_data, dict) else str(breed_data)
            p_breed_lower = p_breed.lower()
            p_type = str(pet.get('type', ''))
            p_age = str(pet.get('age', ''))
            p_gender = str(pet.get('gender', ''))
            p_desc = str(pet.get('description', '') or '').lower()

            if pet_type != "All" and p_type.lower() != pet_type.lower():
                continue
            if age != "All" and p_age.lower() != age.lower():
                continue
            if gender != "All" and p_gender.lower() != gender.lower():
                continue
            if query and not (query in p_name or query in p_breed_lower or query in p_desc):
                continue

            filtered.append(pet)

        return self._wrap_pets(filtered), using_api

    def get_applications(self):
        apps = self.storage.read_json("applications.json")
        return self._wrap_pets(apps)

    def add_application(self, new_app):
        apps = self.get_applications()
        apps.append(new_app)
        return self.storage.write_json("applications.json", apps)

    def update_application_status(self, app_id, status):
        apps = self.get_applications()
        for a in apps:
            if str(a.get("id", a.get("pet_id"))) == str(app_id):
                a["status"] = status
                break
        return self.storage.write_json("applications.json", apps)

    # Aliases
    get_all_applications = get_applications
    load_applications = get_applications
    save_application = add_application
    update_status = update_application_status