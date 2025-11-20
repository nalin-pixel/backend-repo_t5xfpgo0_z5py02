import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import create_document, get_documents, db
from schemas import GasStation, Price

app = FastAPI(title="Gas Station Info API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Gas Station Info API is running"}


# Helpers to convert ObjectId to string

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    _id = d.get("_id")
    if isinstance(_id, ObjectId):
        d["id"] = str(_id)
        del d["_id"]
    return d


# Gas stations

@app.post("/api/stations", response_model=dict)
async def create_station(station: GasStation):
    try:
        inserted_id = create_document("gasstation", station)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StationQuery(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    fuel_type: Optional[str] = None


@app.get("/api/stations", response_model=List[dict])
async def list_stations(city: Optional[str] = None, state: Optional[str] = None, fuel_type: Optional[str] = None, limit: int = 50):
    try:
        filters = {}
        if city:
            filters["city"] = {"$regex": f"^{city}$", "$options": "i"}
        if state:
            filters["state"] = state.upper()
        if fuel_type:
            filters["fuel_types"] = {"$in": [fuel_type.lower()]}
        docs = get_documents("gasstation", filters, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Prices

@app.post("/api/prices", response_model=dict)
async def add_price(price: Price):
    try:
        # ensure station exists
        station_oid = None
        try:
            station_oid = ObjectId(price.station_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid station_id")
        station = db["gasstation"].find_one({"_id": station_oid})
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        inserted_id = create_document("price", price)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prices/{station_id}", response_model=List[dict])
async def get_prices(station_id: str, limit: int = 20):
    try:
        # Validate station id format but don't 404 if station missing; just return []
        try:
            station_oid = ObjectId(station_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid station_id")
        docs = get_documents("price", {"station_id": station_id}, limit)
        return [serialize_doc(d) for d in docs]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
