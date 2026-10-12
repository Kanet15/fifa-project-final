from datetime import datetime

class Pet:
    def __init__(self, pet_id: str, name: str, species: str, breed: str, age: int, 
                 gender: str = "Male", location: str = "Bangkok", description: str = "", 
                 image_url: str = "", status: str = "Available", activity_level: str = "Medium",
                 living_space: str = "Condo", monthly_cost: str = "Medium", 
                 vaccinated: bool = True, scores: dict = None, cost_initial: int = 2000,
                 cost_monthly: int = 1000, tags: list = None):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.gender = gender
        self.location = location
        self.description = description if description else f"น้อง {name} กำลังตามหาบ้านใหม่"
        self.image_url = image_url if image_url else "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600"
        self.status = status
        self.activity_level = activity_level
        self.living_space = living_space
        self.monthly_cost = monthly_cost
        self.vaccinated = vaccinated
        self.scores = scores if scores else {"space": 50, "time": 50, "budget": 50, "exp": 50, "energy": 50}
        self.cost_initial = cost_initial
        self.cost_monthly = cost_monthly
        self.tags = tags if tags else ["น่ารัก"]
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "pet_id": self.pet_id, "name": self.name, "species": self.species,
            "breed": self.breed, "age": self.age, "gender": self.gender,
            "location": self.location, "description": self.description,
            "image_url": self.image_url, "status": self.status,
            "activity_level": self.activity_level, "living_space": self.living_space,
            "monthly_cost": self.monthly_cost, "vaccinated": self.vaccinated,
            "scores": self.scores, "cost_initial": self.cost_initial,
            "cost_monthly": self.cost_monthly, "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            pet_id=data.get("pet_id", "P000"),
            name=data.get("name", "Unknown"),
            species=data.get("species", "Dog"),
            breed=data.get("breed", "Mixed"),
            age=data.get("age", 1),
            gender=data.get("gender", "Male"),
            location=data.get("location", "Bangkok"),
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            status=data.get("status", "Available"),
            activity_level=data.get("activity_level", "Medium"),
            living_space=data.get("living_space", "Condo"),
            monthly_cost=data.get("monthly_cost", "Medium"),
            vaccinated=data.get("vaccinated", True),
            scores=data.get("scores"),
            cost_initial=data.get("cost_initial", 2000),
            cost_monthly=data.get("cost_monthly", 1000),
            tags=data.get("tags")
        )