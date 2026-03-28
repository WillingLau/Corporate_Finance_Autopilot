import json
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from app.services.scraper.yfinance_client import YFinanceClient
from app.services.finance.engine import FinancialEngine
from app.models.forecast import ScenarioAssumptions
from app.core.config import settings

@tool
def generate_financial_forecast(ticker: str, target_net_margin: float = 0.35) -> str:
    """
    Fetch historical financial data and generate projections.
    Accepts a ticker and target_net_margin.
    Returns JSON string with base, upside, and downside forecasts.
    """
    try:
        scraper = YFinanceClient(ticker=ticker)
        company_profile = scraper.fetch_company_data()
        
        assumptions = ScenarioAssumptions(target_net_margin=target_net_margin)
        engine = FinancialEngine()
        forecast_output = engine.run_forecast(company_data=company_profile, assumptions=assumptions)
        
        return forecast_output.model_dump_json(indent=2)
    except Exception as e:
        return f"Error generation forecast: {str(e)}"

search_tool = DuckDuckGoSearchResults(
    name="search_market_news",
    description="Search engine for retrieving the latest business news, queries, and company updates."
)

AGENT_TOOLS = [generate_financial_forecast, search_tool]