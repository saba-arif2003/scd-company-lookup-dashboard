from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class Company(BaseModel):
    """Company information model"""
    name: str = Field(..., description="Company name")
    ticker: str = Field(..., description="Stock ticker symbol", max_length=10)
    cik: str = Field(..., description="SEC Central Index Key")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    industry: Optional[str] = Field(None, description="Company industry")
    sector: Optional[str] = Field(None, description="Company sector")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, description="Company website URL")
    headquarters: Optional[str] = Field(None, description="Company headquarters location")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    employees: Optional[int] = Field(None, description="Number of employees")
    
    @field_validator('ticker')
    @classmethod
    def ticker_must_be_uppercase(cls, v):
        """Ensure ticker is uppercase"""
        return v.upper() if v else v
    
    @field_validator('cik')
    @classmethod
    def validate_cik_format(cls, v):
        """Ensure CIK is 10 digits with leading zeros"""
        if v and len(v) < 10:
            return v.zfill(10)
        return v


class CompanySearchResult(BaseModel):
    """Company search result model"""
    name: str = Field(..., description="Company name")
    ticker: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="SEC Central Index Key") 
    exchange: Optional[str] = Field(None, description="Stock exchange")
    match_score: Optional[float] = Field(None, description="Search relevance score", ge=0, le=1)


class CompanySearchResponse(BaseModel):
    """Company search API response model"""
    query: str = Field(..., description="Original search query")
    results: List[CompanySearchResult] = Field(default_factory=list, description="Search results")
    total_results: int = Field(0, description="Total number of results found")
    took_ms: int = Field(..., description="Search time in milliseconds")
    suggestions: Optional[List[str]] = Field(None, description="Alternative search suggestions")


class CompanyLookupResponse(BaseModel):
    """Complete company lookup response model"""
    company: Company = Field(..., description="Company information")
    stock_quote: Optional[Dict[str, Any]] = Field(None, description="Current stock quote")
    recent_filings: Optional[List[Dict[str, Any]]] = Field(None, description="Recent SEC filings")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Data last updated timestamp")
    data_sources: Dict[str, str] = Field(
        default_factory=lambda: {
            "company_info": "SEC EDGAR",
            "stock_quote": "Yahoo Finance", 
            "filings": "SEC EDGAR"
        },
        description="Data sources used"
    )