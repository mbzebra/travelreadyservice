from fastapi import APIRouter, Depends

from app.models.schemas import ChecklistResponse, TripParameters
from app.services.trip_analyzer import TripAnalyzer
from app.services.checklist_repository import ChecklistRepository


router = APIRouter(prefix="/api/checklist", tags=["Checklist"])


def get_repository() -> ChecklistRepository:
    return ChecklistRepository()


@router.post("/generate", response_model=ChecklistResponse)
async def generate_checklist(
    trip: TripParameters,
    repo: ChecklistRepository = Depends(get_repository),
) -> ChecklistResponse:
    analyzer = TripAnalyzer(trip)
    items = analyzer.generate_checklist()
    response = ChecklistResponse(
        destination=trip.destination_climate,
        trip_type=trip.travel_type,
        travel_mode=trip.travel_mode,
        climate=trip.destination_climate,
        items=items,
    )
    await repo.save_checklist(trip, response)
    return response
