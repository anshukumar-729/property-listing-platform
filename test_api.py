import pytest
from fastapi.testclient import TestClient
from app import app
from services import PropertySearch, PropertyManager

# Create a client for testing
client = TestClient(app)

# Fixture for PropertyManager
@pytest.fixture
def property_manager():
    return PropertyManager()

@pytest.fixture
def property_search(property_manager):
    return PropertySearch(property_manager)

# 1. Test for creating a property
def test_create_property(property_manager):
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    response = client.post("/api/v1/properties", json=property_data)
    assert response.status_code == 200
    assert "property_id" in response.json()

def test_create_property_invalid_input():
    invalid_data = {
        "location": "New York",
        "price": -1000.0,  # Invalid price
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    response = client.post("/api/v1/properties", json=invalid_data)
    assert response.status_code == 422

# 2. Test for updating the property status
def test_update_property_status(property_manager):
    # Create property first
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    property_response = client.post("/api/v1/properties", json=property_data)
    property_id = property_response.json()["property_id"]

    # Update status
    response = client.patch(f"/api/v1/properties/{property_id}/status?status=sold")
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_update_property_status_invalid(property_manager):
    # Invalid property ID
    response = client.patch("/api/v1/properties/invalid_property_id/status?status=sold")
    assert response.status_code == 404
    assert "Property not found" in response.json()["detail"]

def test_update_property_status_unauthorized(property_manager):
    # Create property first
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    property_response = client.post("/api/v1/properties?current_user=other", json=property_data)
    property_id = property_response.json()["property_id"]

    # Attempt to update status with a different user
    response = client.patch(f"/api/v1/properties/{property_id}/status?status=sold")
    assert response.status_code == 403
    assert "Unauthorized access" in response.json()["detail"]

# 3. Test for searching properties
def test_search_properties(property_manager):
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    client.post("/api/v1/properties", json=property_data)

    response = client.get("/api/v1/properties/search?min_price=500&max_price=1500&location=New York&property_type=Apartment&page=1&limit=10")
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0

def test_search_properties_no_results(property_manager):
    response = client.get("/api/v1/properties/search?min_price=5000")
    assert response.status_code == 404
    assert "No properties found matching criteria" in response.json()["detail"]

# 4. Test for shortlisting properties
def test_shortlist_property(property_manager):
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    property_response = client.post("/api/v1/properties", json=property_data)
    property_id = property_response.json()["property_id"]

    response = client.post(f"/api/v1/properties/shortlist/{property_id}")
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_shortlist_property_already_shortlisted(property_manager):
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    property_response = client.post("/api/v1/properties", json=property_data)
    property_id = property_response.json()["property_id"]

    # First shortlist
    client.post(f"/api/v1/properties/shortlist/{property_id}")
    
    # Attempt to shortlist again
    response = client.post(f"/api/v1/properties/shortlist/{property_id}")
    assert response.status_code == 400
    assert "Property already shortlisted" in response.json()["detail"]

# 5. Test for getting shortlisted properties
def test_get_shortlisted_properties(property_manager):
    property_data = {
        "location": "New York",
        "price": 1000.0,
        "property_type": "Apartment",
        "description": "A beautiful apartment",
        "amenities": ["WiFi", "Gym"]
    }
    property_response = client.post("/api/v1/properties", json=property_data)
    property_id = property_response.json()["property_id"]

    # Shortlist property
    client.post(f"/api/v1/properties/shortlist/{property_id}")

    # Fetch shortlisted properties
    response = client.get("/api/v1/properties/shortlisted")
    assert response.status_code == 200
    assert len(response.json()["shortlisted"]) > 0

def test_get_shortlisted_properties_empty(property_manager):
    response = client.get("/api/v1/properties/shortlisted?current_user=other")
    assert response.status_code == 404
    assert "No shortlisted properties found" in response.json()["detail"]
