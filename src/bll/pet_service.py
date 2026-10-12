from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.pet import Pet
from src.dal.json_storage import JSONStorageManager

class PetService:
    def __init__(self, storage: JSONStorageManager):
        self.storage = storage

    def get_all_pets(self) -> List[Pet]:
        data = self.storage.load_data()
        return [Pet.from_dict(item) for item in data]

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        for pet in self.get_all_pets():
            if pet.pet_id == pet_id:
                return pet
        return None

    def calculate_simple_match(self, user_answers: dict) -> List[Dict[str, Any]]:
        pets = self.get_all_pets()
        results = []

        for pet in pets:
            # 1. กรองตามประเภทสัตว์ที่อยากเลี้ยง (ถ้าเลือก)
            if user_answers['species'] != "เปิดรับทุกชนิด" and pet.species != user_answers['species']:
                continue

            score = 100
            reasons = []

            # 2. เช็กสถานที่พักอาศัย
            if user_answers['living_space'] == "คอนโด" and pet.living_space == "House":
                score -= 25
                reasons.append("⚠️ น้องต้องการพื้นที่กว้าง (เหมาะกับบ้านเดี่ยว)")
            else:
                reasons.append("✅ ที่พักอาศัยของคุณเหมาะกับน้อง")

            # 3. เช็กงบประมาณ
            if user_answers['budget'] == "ประหยัด (<1,000 บาท/เดือน)" and pet.cost_monthly > 1000:
                score -= 25
                reasons.append("⚠️ ค่าใช้จ่ายประจำเดือนสูงกว่างบที่เลือกเล็กน้อย")
            else:
                reasons.append("✅ ค่าใช้จ่ายอยู่ในงบประมาณที่คุณรับได้")

            # 4. เช็กเวลาที่มีให้
            if user_answers['time'] == "งานยุ่งมาก (น้อยกว่า 1 ชม./วัน)" and pet.activity_level == "High":
                score -= 30
                reasons.append("⚠️ น้องพลังเยอะและต้องการเวลาดูแลค่อนข้างมาก")
            else:
                reasons.append("✅ เวลาที่คุณมีเหมาะสมกับความต้องการของน้อง")

            # ปรับคะแนนไม่ให้ต่ำกว่า 40%
            final_score = max(40, score)

            results.append({
                "pet": pet,
                "score": final_score,
                "reasons": reasons
            })

        # เรียงตาม % ความเข้ากันได้จากมากไปน้อย
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def submit_application(self, pet_id: str, applicant_name: str, phone: str, 
                           line_id: str, email: str, space_type: str, experience: str, note: str) -> bool:
        apps = self.storage.load_applications()
        new_app = {
            "app_id": f"APP{len(apps) + 1:03d}",
            "pet_id": pet_id,
            "applicant_name": applicant_name,
            "phone": phone,
            "line_id": line_id,
            "email": email,
            "space_type": space_type,
            "experience": experience,
            "note": note,
            "status": "Pending",
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        apps.append(new_app)
        self.storage.save_applications(apps)
        return True

    def get_all_applications(self) -> List[Dict[str, Any]]:
        return self.storage.load_applications()

    def update_app_status(self, app_id: str, new_status: str):
        apps = self.storage.load_applications()
        for app in apps:
            if app["app_id"] == app_id:
                app["status"] = new_status
                break
        self.storage.save_applications(apps)