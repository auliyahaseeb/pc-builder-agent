# src/schema.py
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class PCPart(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
        populate_by_name=True
    )

    category: Literal
    name: str = Field(..., description="Standardized manufacturer nomenclature")
    price: float = Field(..., gt=0, description="Real-time market price in USD")
    vendor: str = Field(..., description="Retailer name (e.g., Amazon, Newegg)")
    wattage: int = Field(0, ge=0, description="Max TDP under load in watts")
    
    # Technological attributes
    socket: Optional[str] = Field(None, description="Socket type: AM4, AM5, LGA1700, LGA1851")
    chipset: Optional[str] = Field(None, description="Motherboard chipset: B650, Z890, etc.")
    memory_type: Optional] = Field(None, description="RAM generation")
    form_factor: Optional[str] = Field(None, description="ATX, Micro-ATX, Mini-ITX, SFX, etc.")
    
    # Physical dimensions (LxWxH in millimeters)
    dimensions: Optional, int]] = Field(
        None, description="Dimensions in mm"
    )
    max_gpu_length: Optional[int] = Field(None, description="For cases: Max GPU length in mm")
    max_cooler_height: Optional[int] = Field(None, description="For cases: Max CPU cooler height in mm")

class FullBuild(BaseModel):
    model_config = ConfigDict(extra='forbid')

    components: List[PCPart] = Field(..., description="List of all selected components")
    total_price: float = Field(0.0, description="Aggregate cost")
    total_tdp: int = Field(0, description="Aggregate power draw")
    is_compatible: bool = Field(False, description="Result of the validator logic")
    build_notes: List[str] = Field(default_factory=list, description="Warnings or arbitrage alerts")

    @model_validator(mode='after')
    def calculate_totals(self) -> 'FullBuild':
        self.total_price = round(sum(part.price for part in self.components), 2)
        self.total_tdp = sum(part.wattage for part in self.components)
        return self