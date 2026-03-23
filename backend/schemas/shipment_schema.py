from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime

# ✅ Base structure shared by Create, Out
class ShipmentBase(BaseModel):
    pickup_location: str
    dropoff_location: str
    trailer_type: Optional[str] = None
    rate: Optional[float] = Field(default=None)
    weight: Optional[Union[str, float]] = None
    length: Optional[Union[str, float]] = None
    load_size: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "Draft"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    recurring_type: Optional[str] = None
    days: Optional[str] = None

# ✅ Used when creating new shipment
class ShipmentCreate(ShipmentBase):
    user_id: int  # Required only at creation

# ✅ Used for updating shipment fields (partial update)
class ShipmentUpdate(BaseModel):
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    trailer_type: Optional[str] = None
    rate: Optional[float] = None
    weight: Optional[Union[str, float]] = None
    length: Optional[Union[str, float]] = None
    load_size: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    recurring_type: Optional[str] = None
    days: Optional[str] = None
    # Do not include user_id here because it is not editable

# ✅ Response output model
class ShipmentOut(ShipmentBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
