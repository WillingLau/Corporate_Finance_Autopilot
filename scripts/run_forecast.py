import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.scraper.yfinance_client import YFinanceClient
from app.services.finance.engine import FinancialEngine
from app.models.forecast import ScenarioAssumptions
from app.core.config import settings

def main():
    print("Fetching historical data...")
    scraper = YFinanceClient(ticker=settings.TARGET_TICKER)
    company_profile = scraper.fetch_company_data()
    
    print("\nRunning financial models...")
    assumptions = ScenarioAssumptions(
        target_net_margin=0.40,
        forecast_years=3
    )
    
    engine = FinancialEngine()
    try:
        forecast_output = engine.run_forecast(company_data=company_profile, assumptions=assumptions)
        
        print(f"\nForecast complete. Historical CAGR: {forecast_output.historical_cagr:.2%}")
        
        print(f"\nUpside Case (Growth Rate: {forecast_output.upside_case.assumed_growth_rate:.2%}):")
        for year_data in forecast_output.upside_case.forecast_data:
            print(f"  {year_data.year}: Rev=${year_data.total_revenue:,.0f}, Net=${year_data.net_income:,.0f}")
            
        print(f"\nDownside Case (Growth Rate: {forecast_output.downside_case.assumed_growth_rate:.2%}):")
        for year_data in forecast_output.downside_case.forecast_data:
            print(f"  {year_data.year}: Rev=${year_data.total_revenue:,.0f}, Net=${year_data.net_income:,.0f}")

    except Exception as e:
        print(f"\nExecution failed: {e}")

if __name__ == "__main__":
    main()