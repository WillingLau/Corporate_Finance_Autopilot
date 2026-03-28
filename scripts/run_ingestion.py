import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.scraper.yfinance_client import YFinanceClient
from app.core.config import settings

def main():
    print("Starting data ingestion pipeline...")
    
    client = YFinanceClient(ticker=settings.TARGET_TICKER)
    
    try:
        company_profile = client.fetch_company_data()
        
        print("\nData fetched successfully:")
        print(company_profile.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"\nPipeline execution failed: {e}")

if __name__ == "__main__":
    main()