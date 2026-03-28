from pydantic import BaseModel, Field
from typing import List, Optional

class YearlyFinancials(BaseModel):
    year: str = Field(..., description="Financial year, e.g. '2023'")
    total_revenue: float = Field(..., description="Total Revenue")
    net_income: float = Field(..., description="Net Income")
    operating_income: Optional[float] = Field(None, description="Operating Income")

class CompanyProfile(BaseModel):
    ticker: str = Field(..., description="Stock Ticker")
    company_name: str = Field(..., description="Company Name")
    sector: str = Field(..., description="Sector")
    business_summary: str = Field(..., description="Business Summary")
    historical_financials: List[YearlyFinancials] = Field(default_factory=list, description="Yearly financial data")