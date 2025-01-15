from typing import List
from fastapi import HTTPException
from datetime import datetime
import uuid
from typing import List, Dict
from threading import Lock

class Property:
    def __init__(self, property_id: str, user_id: str, details: dict):
        self.property_id = property_id
        self.user_id = user_id
        self.details = details
        self.status = "available"
        self.timestamp = datetime.now()

class PropertyManager:
    def __init__(self):
        self.properties: Dict[str, Property] = {}
        self.user_portfolios: Dict[str, List[str]] = {}
        self.lock = Lock()

    def add_property(self, user_id: str, property_details: dict) -> str:
        property_id = str(uuid.uuid4())
        new_property = Property(property_id, user_id, property_details)
        self.properties[property_id] = new_property

        if user_id not in self.user_portfolios:
            self.user_portfolios[user_id] = []
        self.user_portfolios[user_id].append(property_id)

        return property_id

    def update_property_status(self, property_id: str, status: str, user_id: str) -> bool:
        property_obj = self.properties.get(property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        if property_obj.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        property_obj.status = status
        return True

    def get_user_properties(self, user_id: str) -> List[Property]:
        property_ids = self.user_portfolios.get(user_id, [])
        return [
            self.properties[pid]
            for pid in property_ids
            if self.properties[pid].status == "available"
        ]

class PropertySearch:
    def __init__(self, property_manager: PropertyManager):
        self.property_manager = property_manager

    def search_properties(self, criteria: dict) -> List[Property]:
        results = []
        for property_obj in self.property_manager.properties.values():
            if self._match_criteria(property_obj, criteria):
                results.append(property_obj)
        return results

    def shortlist_property(self, user_id: str, property_id: str) -> bool:
        with self.property_manager.lock:
            property_obj = self.property_manager.properties.get(property_id)
            if not property_obj:
                raise HTTPException(status_code=404, detail="Property not found")
            if "shortlisted_by" not in property_obj.details:
                property_obj.details["shortlisted_by"] = []
            if user_id in property_obj.details["shortlisted_by"]:
                raise HTTPException(status_code=400, detail="Property already shortlisted")
            property_obj.details["shortlisted_by"].append(user_id)
            return True

    def get_shortlisted(self, user_id: str) -> List[Property]:
        shortlisted = []
        for property_obj in self.property_manager.properties.values():
            if user_id in property_obj.details.get("shortlisted_by", []):
                if property_obj.status == "available":
                    shortlisted.append(property_obj)
        return shortlisted

    def _match_criteria(self, property_obj: Property, criteria: dict) -> bool:
        if (
            criteria.get("min_price")
            and property_obj.details.get("price") < criteria["min_price"]
        ):
            return False
        if (
            criteria.get("max_price")
            and property_obj.details.get("price") > criteria["max_price"]
        ):
            return False
        if (
            criteria.get("location")
            and property_obj.details.get("location") != criteria["location"]
        ):
            return False
        if (
            criteria.get("property_type")
            and property_obj.details.get("property_type") != criteria["property_type"]
        ):
            return False
        return True
