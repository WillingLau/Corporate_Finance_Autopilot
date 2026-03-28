import pytest
from app.models.forecast import ScenarioAssumptions
from app.services.finance.engine import FinancialEngine

# Hand-written mock class to bypass engine's type and method checks
class DummyRecord:
    def __init__(self, year, total_revenue, net_income):
        self.year = year
        self.total_revenue = float(total_revenue)
        self.net_income = float(net_income)
    
    # Compatible with Pydantic v2 methods
    def model_dump(self):
        return {"year": self.year, "total_revenue": self.total_revenue, "net_income": self.net_income}
    
    # Compatible with dictionary access
    def __getitem__(self, item):
        return getattr(self, item)

class DummyCompany:
    def __init__(self, ticker, historical_financials):
        self.ticker = ticker
        self.historical_financials = historical_financials

def test_financial_engine_growth_calculation():
    # Arrange: Provide 3 years of perfect staircase growth data
    mock_company = DummyCompany(
        ticker="TEST",
        historical_financials=[
            DummyRecord(year=2021, total_revenue=100.0, net_income=20.0),
            DummyRecord(year=2022, total_revenue=110.0, net_income=22.0),
            DummyRecord(year=2023, total_revenue=121.0, net_income=24.2)
        ]
    )
    
    assumptions = ScenarioAssumptions(
        target_net_margin=0.20,
        upside_modifier=0.05,
        downside_modifier=-0.05
    )
    
    engine = FinancialEngine()
    
    # Act
    result = engine.run_forecast(mock_company, assumptions)
    
    # Assert
    assert abs(result.historical_cagr - 0.10) < 0.01  # Growth rate should solidly be 10%
    assert len(result.base_case.forecast_data) == 3   # Successfully forecasted next 3 years

def test_financial_engine_insufficient_data():
    # Arrange: Only 1 year of data, triggers failure
    mock_company = DummyCompany(
        ticker="TEST",
        historical_financials=[DummyRecord(year=2023, total_revenue=100.0, net_income=20.0)]
    )
    assumptions = ScenarioAssumptions()
    engine = FinancialEngine()
    
    # Act & Assert: Must raise exception
    with pytest.raises(Exception):
        engine.run_forecast(mock_company, assumptions)