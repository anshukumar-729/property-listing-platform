from fastapi import APIRouter, Query, HTTPException
from services import PropertySearch, PropertyManager
from models import PropertyCreate

router = APIRouter()

property_manager = PropertyManager()
property_search = PropertySearch(property_manager)

@router.post("/api/v1/properties")
async def create_property(property_data: PropertyCreate, current_user: str = Query("test_user")):
    user_id = current_user
    try:
        property_details = property_data.dict()
        property_id = property_manager.add_property(user_id, property_details)
        return {"property_id": property_id}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

@router.patch("/api/v1/properties/{property_id}/status")
async def update_property_status(property_id: str, status: str, current_user: str = Query("test_user")):
    try:
        success = property_manager.update_property_status(property_id, status, current_user)
        return {"success": success}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/api/v1/properties/search")
async def search_properties(min_price: float = Query(None, gt=0), max_price: float = Query(None, gt=0),
                            location: str = Query(None), property_type: str = Query(None),
                            page: int = Query(1, gt=0), limit: int = Query(10, gt=0)):
    criteria = {
        "min_price": min_price,
        "max_price": max_price,
        "location": location,
        "property_type": property_type,
    }
    results = property_search.search_properties(criteria)
    if not results:
        raise HTTPException(status_code=404, detail="No properties found matching criteria")
    start = (page - 1) * limit
    end = start + limit
    paginated_results = results[start:end]
    return {
        "results": [
            {"property_id": p.property_id, "details": p.details, "status": p.status}
            for p in paginated_results
        ],
        "total": len(results),
    }

@router.post("/api/v1/properties/shortlist/{property_id}")
async def shortlist_property(property_id: str, current_user: str = Query("test_user")):
    try:
        success = property_search.shortlist_property(current_user, property_id)
        return {"success": success}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/api/v1/properties/shortlisted")
async def get_shortlisted_properties(current_user: str = Query("test_user")):
    shortlisted = property_search.get_shortlisted(current_user)
    if not shortlisted:
        raise HTTPException(status_code=404, detail="No shortlisted properties found")
    return {
        "shortlisted": [
            {"property_id": p.property_id, "details": p.details, "status": p.status}
            for p in shortlisted
        ]
    }
