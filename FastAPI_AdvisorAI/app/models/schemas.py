# app/models/schemas.py
from pydantic import BaseModel

class ClientProfile(BaseModel):
    age: int
    annual_income: float
    dependents: int
    location: str
    total_debt: float
    available_savings: float
    existing_life_insurance: float
    income_replacement_years: int
    currency: str = "USD"
