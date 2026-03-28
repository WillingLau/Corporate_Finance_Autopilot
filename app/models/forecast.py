from pydantic import BaseModel, Field
from typing import List
from app.models.finance import YearlyFinancials

class ScenarioAssumptions(BaseModel):
    forecast_years: int = Field(3, description="Number of years to forecast")
    base_revenue_cagr_modifier: float = Field(0.0, description="Base CAGR modifier")
    upside_modifier: float = Field(0.05, description="Upside growth rate modifier")
    downside_modifier: float = Field(-0.05, description="Downside growth rate modifier")
    target_net_margin: float = Field(0.35, description="Target net margin")

class ScenarioResult(BaseModel):
    scenario_name: str = Field(..., description="Scenario Name")
    assumed_growth_rate: float = Field(..., description="Assumed revenue growth rate")
    forecast_data: List[YearlyFinancials] = Field(..., description="Projected financial data")

class FinancialModelOutput(BaseModel):
    historical_cagr: float = Field(..., description="Historical CAGR")
    base_case: ScenarioResult
    upside_case: ScenarioResult
    downside_case: ScenarioResult