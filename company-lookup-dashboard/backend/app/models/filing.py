from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class FilingFormType(str, Enum):
    """Common SEC filing form types"""
    FORM_10K = "10-K"         # Annual report
    FORM_10Q = "10-Q"         # Quarterly report  
    FORM_8K = "8-K"           # Current report
    FORM_DEF_14A = "DEF 14A"  # Proxy statement
    FORM_S1 = "S-1"           # Registration statement
    FORM_S3 = "S-3"           # Registration statement
    FORM_4 = "4"              # Insider trading
    FORM_3 = "3"              # Initial insider filing
    FORM_5 = "5"              # Annual insider summary
    FORM_SC_13G = "SC 13G"    # Beneficial ownership
    FORM_SC_13D = "SC 13D"    # Beneficial ownership
    FORM_11K = "11-K"         # Employee stock purchase plan
    FORM_20F = "20-F"         # Foreign company annual report
    OTHER = "OTHER"


class Filing(BaseModel):
    """SEC filing model"""
    form: str = Field(..., description="Filing form type (e.g., 10-K, 10-Q, 8-K)")
    filing_date: date = Field(..., description="Date the filing was submitted to SEC")
    accession_number: str = Field(..., description="SEC accession number")
    filing_url: str = Field(..., description="URL to the filing document")  # Changed from HttpUrl to str
    company_name: Optional[str] = Field(None, description="Company name from filing")
    cik: Optional[str] = Field(None, description="SEC Central Index Key")
    
    # Additional filing metadata
    file_size: Optional[int] = Field(None, description="Filing document size in bytes")
    document_count: Optional[int] = Field(None, description="Number of documents in filing")
    period_end_date: Optional[date] = Field(None, description="Reporting period end date")
    
    # Filing details
    description: Optional[str] = Field(None, description="Filing description/title")
    is_xbrl: Optional[bool] = Field(None, description="Whether filing includes XBRL data")
    is_inline_xbrl: Optional[bool] = Field(None, description="Whether filing uses inline XBRL")
    
    @field_validator('form')
    @classmethod
    def validate_form_type(cls, v):
        """Validate and normalize form type"""
        if v:
            v = v.upper().replace('-', '-')  # Normalize dashes
            # Map common variations
            form_mappings = {
                '10K': '10-K',
                '10Q': '10-Q',
                '8K': '8-K',
                'DEF14A': 'DEF 14A',
                'SC13G': 'SC 13G',
                'SC13D': 'SC 13D'
            }
            return form_mappings.get(v, v)
        return v
    
    @field_validator('accession_number')
    @classmethod
    def validate_accession_number(cls, v):
        """Validate SEC accession number format"""
        if v and not v.count('-') == 2:
            # Try to format if it's just digits
            if v.isdigit() and len(v) == 18:
                return f"{v[:10]}-{v[10:12]}-{v[12:]}"
        return v
    
    @property
    def form_type_category(self) -> str:
        """Get the category of the filing form"""
        if self.form in ['10-K', '10-Q']:
            return 'Financial Report'
        elif self.form == '8-K':
            return 'Current Report'
        elif self.form in ['3', '4', '5']:
            return 'Insider Trading'
        elif self.form in ['DEF 14A']:
            return 'Proxy Statement'
        elif self.form in ['S-1', 'S-3']:
            return 'Registration'
        elif self.form in ['SC 13G', 'SC 13D']:
            return 'Beneficial Ownership'
        else:
            return 'Other'
    
    @property
    def is_major_report(self) -> bool:
        """Check if this is a major financial report"""
        return self.form in ['10-K', '10-Q', '8-K']
    
    class Config:
        json_schema_extra = {
            "example": {
                "form": "10-Q",
                "filing_date": "2024-07-24",
                "accession_number": "0001628280-24-027353",
                "filing_url": "https://www.sec.gov/Archives/edgar/data/1318605/000162828024027353/tsla-20240630.htm",
                "company_name": "Tesla Inc",
                "cik": "0001318605",
                "file_size": 1234567,
                "document_count": 15,
                "period_end_date": "2024-06-30",
                "description": "Quarterly report pursuant to Section 13 or 15(d)",
                "is_xbrl": True,
                "is_inline_xbrl": True
            }
        }


class FilingResponse(BaseModel):
    """SEC filings API response model"""
    cik: str = Field(..., description="SEC Central Index Key")
    company_name: Optional[str] = Field(None, description="Company name")
    filings: List[Filing] = Field(default_factory=list, description="List of SEC filings")
    total_filings: int = Field(0, description="Total number of filings available")
    filings_returned: int = Field(0, description="Number of filings in this response")
    date_range: Optional[Dict[str, date]] = Field(None, description="Date range of filings")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Data last updated timestamp")
    
    @field_validator('filings_returned', mode='after')
    @classmethod
    def set_filings_returned(cls, v, info):
        """Automatically set filings_returned based on filings list length"""
        if hasattr(info, 'data') and 'filings' in info.data:
            return len(info.data['filings'])
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "cik": "0001318605",
                "company_name": "Tesla Inc",
                "filings": [
                    {
                        "form": "10-Q",
                        "filing_date": "2024-07-24", 
                        "accession_number": "0001628280-24-027353",
                        "filing_url": "https://www.sec.gov/Archives/edgar/data/1318605/000162828024027353/tsla-20240630.htm",
                        "period_end_date": "2024-06-30"
                    }
                ],
                "total_filings": 245,
                "filings_returned": 1,
                "date_range": {
                    "earliest": "2010-01-29",
                    "latest": "2024-07-24"
                },
                "last_updated": "2024-08-27T10:30:00Z"
            }
        }


class FilingSearchCriteria(BaseModel):
    """Criteria for searching SEC filings"""
    cik: Optional[str] = Field(None, description="SEC Central Index Key")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol") 
    form_types: Optional[List[str]] = Field(None, description="List of form types to include")
    date_from: Optional[date] = Field(None, description="Start date for filing search")
    date_to: Optional[date] = Field(None, description="End date for filing search")
    limit: Optional[int] = Field(10, description="Maximum number of filings to return", ge=1, le=100)
    include_amendments: Optional[bool] = Field(True, description="Include amended filings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cik": "0001318605",
                "form_types": ["10-K", "10-Q", "8-K"],
                "date_from": "2024-01-01",
                "date_to": "2024-08-27",
                "limit": 10,
                "include_amendments": True
            }
        }