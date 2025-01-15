from pydantic import BaseModel, Field
from typing import List

    
class PropertyCreate(BaseModel):
    location: str = Field(..., description="Location of the property")
    price: float = Field(..., gt=0, description="Price of the property")
    property_type: str = Field(..., description="Type of the property")
    description: str = Field(..., description="Detailed description of the property")
    amenities: List[str] = Field(..., description="List of amenities provided")
