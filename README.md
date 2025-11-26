# Travel Ready Service

A FastAPI and MongoDB-based checklist generation engine that builds contextual travel packing lists from trip parameters.

## Features
- TripAnalyzer service merges climate, travel type, travel mode, duration, and traveler demographics to generate 50-100 prioritized items.
- Scoring system flags each item as critical, high, medium, or nice-to-have based on weighted rules.
- MongoDB persistence stores trip requests and generated checklists for auditing and reuse.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set MongoDB connection (optional — defaults to `mongodb://localhost:27017` and database `travelready`):
   ```bash
   export MONGODB_URI="mongodb://localhost:27017"
   export MONGODB_DB="travelready"
   ```

3. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Generate a checklist:
   ```bash
   curl -X POST http://localhost:8000/api/checklist/generate \
     -H "Content-Type: application/json" \
     -d '{
       "origin_climate": "temperate",
       "destination_climate": "tropical",
       "duration_days": 8,
       "season": "summer",
       "travel_type": "leisure",
       "travel_mode": "air",
       "traveler_demographics": [{"age_group": "adult"}]
     }'
   ```

The response includes contextualized items with scores and rationales.
