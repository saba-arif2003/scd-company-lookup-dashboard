from datetime import datetime, date, timedelta
from typing import Optional, Union
import re
import math


def format_currency(
    value: Optional[Union[int, float]], 
    currency: str = "USD", 
    decimal_places: int = 2
) -> Optional[str]:
    """Format a number as currency"""
    if value is None:
        return None
    
    try:
        # Handle large numbers with appropriate suffixes
        if abs(value) >= 1_000_000_000_000:  # Trillion
            formatted_value = f"${value / 1_000_000_000_000:.{decimal_places}f}T"
        elif abs(value) >= 1_000_000_000:  # Billion
            formatted_value = f"${value / 1_000_000_000:.{decimal_places}f}B"
        elif abs(value) >= 1_000_000:  # Million
            formatted_value = f"${value / 1_000_000:.{decimal_places}f}M"
        elif abs(value) >= 1_000:  # Thousand
            formatted_value = f"${value / 1_000:.{decimal_places}f}K"
        else:
            formatted_value = f"${value:.{decimal_places}f}"
        
        return formatted_value if currency == "USD" else f"{formatted_value} {currency}"
    
    except (TypeError, ValueError):
        return None


def format_percentage(
    value: Optional[Union[int, float]], 
    decimal_places: int = 2,
    include_sign: bool = True
) -> Optional[str]:
    """Format a number as percentage"""
    if value is None:
        return None
    
    try:
        formatted = f"{value:.{decimal_places}f}%"
        
        if include_sign and value > 0:
            formatted = f"+{formatted}"
        
        return formatted
    
    except (TypeError, ValueError):
        return None


def format_large_number(
    value: Optional[Union[int, float]],
    decimal_places: int = 1
) -> Optional[str]:
    """Format large numbers with K/M/B/T suffixes"""
    if value is None:
        return None
    
    try:
        if abs(value) >= 1_000_000_000_000:  # Trillion
            return f"{value / 1_000_000_000_000:.{decimal_places}f}T"
        elif abs(value) >= 1_000_000_000:  # Billion
            return f"{value / 1_000_000_000:.{decimal_places}f}B"
        elif abs(value) >= 1_000_000:  # Million
            return f"{value / 1_000_000:.{decimal_places}f}M"
        elif abs(value) >= 1_000:  # Thousand
            return f"{value / 1_000:.{decimal_places}f}K"
        else:
            return f"{int(value) if value == int(value) else value:.{decimal_places}f}"
    
    except (TypeError, ValueError):
        return None


def parse_date_string(date_str: str, formats: list = None) -> Optional[date]:
    """Parse date string with multiple possible formats"""
    if not date_str:
        return None
    
    if formats is None:
        formats = [
            "%Y-%m-%d",      # 2024-01-15
            "%m/%d/%Y",      # 01/15/2024
            "%d/%m/%Y",      # 15/01/2024
            "%Y/%m/%d",      # 2024/01/15
            "%B %d, %Y",     # January 15, 2024
            "%b %d, %Y",     # Jan 15, 2024
            "%d %B %Y",      # 15 January 2024
            "%d %b %Y",      # 15 Jan 2024
            "%Y%m%d",        # 20240115
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculate number of business days between two dates"""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Monday = 0, Sunday = 6
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def normalize_company_name(name: str) -> str:
    """Normalize company name for comparison"""
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove common suffixes and prefixes
    suffixes_to_remove = [
        "inc", "inc.", "incorporated",
        "corp", "corp.", "corporation",
        "ltd", "ltd.", "limited",
        "llc", "l.l.c.",
        "co", "co.", "company",
        "plc", "p.l.c."
    ]
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(f" {suffix}"):
            normalized = normalized[:-len(suffix)-1].strip()
        elif normalized.endswith(f".{suffix}"):
            normalized = normalized[:-len(suffix)-1].strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized


def calculate_percentage_change(old_value: float, new_value: float) -> Optional[float]:
    """Calculate percentage change between two values"""
    if old_value is None or new_value is None or old_value == 0:
        return None
    
    try:
        return ((new_value - old_value) / old_value) * 100
    except (TypeError, ZeroDivisionError):
        return None


def is_market_hours(timezone: str = "US/Eastern") -> bool:
    """Check if current time is during market hours"""
    try:
        from zoneinfo import ZoneInfo
        import datetime as dt
        
        # Get current time in Eastern timezone
        eastern = ZoneInfo(timezone)
        now = dt.datetime.now(eastern)
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Market hours: 9:30 AM - 4:00 PM Eastern
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    except ImportError:
        # Fallback if zoneinfo is not available
        return True  # Assume market is open


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length with optional suffix"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_numbers_from_string(text: str) -> list:
    """Extract all numbers from a string"""
    if not text:
        return []
    
    # Find all numbers (including decimals)
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    # Convert to appropriate numeric types
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        except ValueError:
            continue
    
    return numbers


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default on division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def round_to_significant_figures(value: float, sig_figs: int = 3) -> float:
    """Round a number to specified significant figures"""
    if value == 0:
        return 0
    
    try:
        return round(value, -int(math.floor(math.log10(abs(value)))) + (sig_figs - 1))
    except (ValueError, OverflowError):
        return value


def generate_hash_id(text: str, length: int = 8) -> str:
    """Generate a short hash ID from text"""
    import hashlib
    
    hash_obj = hashlib.md5(text.encode())
    return hash_obj.hexdigest()[:length]


def chunks(lst: list, chunk_size: int):
    """Yield successive chunks from a list"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def deep_get(dictionary: dict, keys: str, default=None):
    """Get nested dictionary value using dot notation"""
    try:
        keys_list = keys.split('.')
        value = dictionary
        
        for key in keys_list:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    except (AttributeError, TypeError):
        return default