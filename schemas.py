"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (retain for reference/examples)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Gas station app schemas

class GasStation(BaseModel):
    """
    Gas stations collection schema
    Collection name: "gasstation"
    """
    name: str = Field(..., description="Station name")
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., min_length=2, max_length=2, description="State code")
    zip_code: Optional[str] = Field(None, description="ZIP/Postal code")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    phone: Optional[str] = Field(None, description="Phone number")
    fuel_types: List[str] = Field(default_factory=list, description="Available fuel types, e.g., ['regular','midgrade','premium','diesel']")
    amenities: List[str] = Field(default_factory=list, description="Amenities like car_wash, air_pump, atm, restroom")
    open_24_hours: bool = Field(False, description="Open 24 hours")
    hours: Optional[str] = Field(None, description="Opening hours description")

class Price(BaseModel):
    """
    Fuel price reports collection
    Collection name: "price"
    """
    station_id: str = Field(..., description="ID of the gas station")
    fuel_type: str = Field(..., description="Fuel type: regular | midgrade | premium | diesel")
    price: float = Field(..., gt=0, description="Price per gallon" )
    source: Optional[str] = Field(None, description="Source of the price (user, web, sign)")
