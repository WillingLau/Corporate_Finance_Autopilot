import pandas as pd
from unittest.mock import patch, MagicMock
from app.services.scraper.yfinance_client import YFinanceClient

@patch("app.services.scraper.yfinance_client.yf.Ticker")
def test_yfinance_client_fetch(mock_ticker_class):
    # Arrange
    mock_instance = MagicMock()
    
    mock_instance.info = {
        "symbol": "TEST",
        "shortName": "Test Corp",
        "longName": "Test Corporation",
        "sector": "Technology",
        "industry": "Software",
        "longBusinessSummary": "A mock company for testing."
    }
    
    # Critical fix: Use pd.Timestamp as column names to perfectly mock real financial statement timestamps!
    mock_df = pd.DataFrame(
        {pd.Timestamp("2023-12-31"): [1000.0, 200.0]},
        index=["Total Revenue", "Net Income"]
    )
    mock_instance.financials = mock_df
    
    # Complete other potentially accessed attributes to prevent AttributeError
    mock_instance.balance_sheet = pd.DataFrame()
    mock_instance.cashflow = pd.DataFrame()
    mock_instance.news = [{"title": "Test News", "publisher": "Test"}]
    
    mock_ticker_class.return_value = mock_instance
    client = YFinanceClient(ticker="TEST")
    
    # Act
    result = client.fetch_company_data()
    
    # Assert
    assert result is not None
    # Critical fix: Change dictionary syntax to Pydantic object dot notation syntax
    assert result.ticker == "TEST"
    assert result.sector == "Technology"