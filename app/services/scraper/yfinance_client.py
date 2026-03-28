import yfinance as yf
import pandas as pd
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.models.finance import CompanyProfile, YearlyFinancials

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YFinanceClient:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self._stock = yf.Ticker(self.ticker)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_company_data(self) -> CompanyProfile:
        logger.info(f"Fetching data for {self.ticker}...")
        
        try:
            info = self._stock.info
            company_name = info.get("shortName", self.ticker)
            sector = info.get("sector", "Unknown")
            business_summary = info.get("longBusinessSummary", "")

            financials: pd.DataFrame = self._stock.financials
            
            if financials is None or financials.empty:
                raise ValueError(f"No financial data found for {self.ticker}.")

            historical_data = []
            
            for col in financials.columns[:4]:
                year_str = str(col.year)
                
                def safe_get(metric_name: str) -> float:
                    try:
                        val = financials.loc[metric_name, col]
                        return float(val) if pd.notna(val) else 0.0
                    except KeyError:
                        return 0.0

                yearly_data = YearlyFinancials(
                    year=year_str,
                    total_revenue=safe_get("Total Revenue"),
                    net_income=safe_get("Net Income"),
                    operating_income=safe_get("Operating Income")
                )
                historical_data.append(yearly_data)

            historical_data.sort(key=lambda x: x.year)

            profile = CompanyProfile(
                ticker=self.ticker,
                company_name=company_name,
                sector=sector,
                business_summary=business_summary,
                historical_financials=historical_data
            )
            
            logger.info(f"Data retrieved for {self.ticker} ({len(historical_data)} years).")
            return profile

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise