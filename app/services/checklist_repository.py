from typing import Any, Dict

from app.db import database
from app.models.schemas import ChecklistResponse, TripParameters


class ChecklistRepository:
    def __init__(self) -> None:
        self.collection = database.get_collection("checklists")

    async def save_checklist(self, params: TripParameters, response: ChecklistResponse) -> None:
        payload: Dict[str, Any] = {
            "trip": params.dict(),
            "response": response.dict(),
        }
        await self.collection.insert_one(payload)
