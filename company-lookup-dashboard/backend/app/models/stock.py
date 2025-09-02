from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class StockQuote(BaseModel):
    """Stock quote model"""
    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current stock price", gt=0)
    currency: str = Field(default="USD", description="Price currency")
    change: Optional[float] = Field(None, description="Price change from previous close")
    change_percent: Optional[float] = Field(None, description="Percentage change from previous close")
    volume: Optional[int] = Field(None, description="Trading volume", ge=0)
    market_cap: Optional[float] = Field(None, description="Market capitalization", ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Quote timestamp")
    market_state: Optional[str] = Field(None, description="Market state (REGULAR, CLOSED, PRE, POST)")
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_uppercase(cls, v):
        """Ensure symbol is uppercase"""
        return v.upper() if v else v
    
    @field_validator('currency')
    @classmethod
    def currency_must_be_uppercase(cls, v):
        """Ensure currency is uppercase"""
        return v.upper() if v else v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate price is reasonable"""
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        if v > 1000000:  # $1M per share seems unreasonable
            raise ValueError('Price seems unreasonably high')
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TSLA",
                "price": 248.50,
                "currency": "USD",
                "change": -5.25,
                "change_percent": -2.07,
                "volume": 45234567,
                "market_cap": 789123456789,
                "last_updated": "2024-08-27T15:30:00Z",
                "market_state": "REGULAR"
            }
        }


class StockData(BaseModel):
    """Extended stock data model"""
    quote: StockQuote = Field(..., description="Current stock quote")
    
    # Trading data
    open_price: Optional[float] = Field(None, description="Opening price")
    high_price: Optional[float] = Field(None, description="Day high price")
    low_price: Optional[float] = Field(None, description="Day low price")
    previous_close: Optional[float] = Field(None, description="Previous closing price")
    
    # Volume data
    avg_volume: Optional[int] = Field(None, description="Average trading volume")
    volume_ratio: Optional[float] = Field(None, description="Current volume vs average volume ratio")
    
    # Price ranges
    fifty_two_week_high: Optional[float] = Field(None, description="52-week high price")
    fifty_two_week_low: Optional[float] = Field(None, description="52-week low price")
    
    # Financial metrics
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    eps: Optional[float] = Field(None, description="Earnings per share")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    
    # Company metrics
    shares_outstanding: Optional[int] = Field(None, description="Number of shares outstanding")
    float_shares: Optional[int] = Field(None, description="Number of floating shares")
    
    # Market data
    beta: Optional[float] = Field(None, description="Stock beta (volatility measure)")
    
    # Timestamps
    earnings_date: Optional[date] = Field(None, description="Next earnings announcement date")
    ex_dividend_date: Optional[date] = Field(None, description="Ex-dividend date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quote": {
                    "symbol": "TSLA",
                    "price": 248.50,
                    "currency": "USD",
                    "change": -5.25,
                    "change_percent": -2.07,
                    "volume": 45234567,
                    "market_cap": 789123456789,
                    "market_state": "REGULAR"
                },
                "open_price": 252.10,
                "high_price": 254.30,
                "low_price": 246.80,
                "previous_close": 253.75,
                "avg_volume": 89567234,
                "volume_ratio": 0.51,
                "fifty_two_week_high": 414.50,
                "fifty_two_week_low": 138.80,
                "pe_ratio": 62.45,
                "eps": 3.98,
                "dividend_yield": None,
                "shares_outstanding": 3178000000,
                "beta": 2.24,
                "earnings_date": "2024-10-23"
            }
        }


class StockHistoricalData(BaseModel):
    """Historical stock price data"""
    symbol: str = Field(..., description="Stock ticker symbol")
    date: date = Field(..., description="Trading date")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    adj_close: Optional[float] = Field(None, description="Adjusted closing price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TSLA",
                "date": "2024-08-26",
                "open": 252.10,
                "high": 254.30,
                "low": 246.80,
                "close": 253.75,
                "volume": 45234567,
                "adj_close": 253.75
            }
        }