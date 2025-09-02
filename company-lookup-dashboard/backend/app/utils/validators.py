import re
from typing import Optional
from datetime import datetime, date
import string


def is_valid_ticker(ticker: str) -> bool:
    """Validate stock ticker symbol format"""
    if not ticker:
        return False
    
    # Pattern: 1-5 uppercase letters, optionally followed by dot and 1-2 letters
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    return bool(re.match(pattern, ticker.upper()))


def is_valid_cik(cik: str) -> bool:
    """Validate SEC CIK format"""
    if not cik:
        return False
    
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, cik))
    
    # CIK should be 1-10 digits
    return len(digits_only) >= 1 and len(digits_only) <= 10


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    pattern = r'^https?://'
    return bool(re.match(pattern, url, re.IGNORECASE))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # US phone numbers should have 10 or 11 digits
    return len(digits_only) in [10, 11]


def is_valid_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """Validate date string format"""
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def is_valid_date_range(start_date: str, end_date: str, date_format: str = "%Y-%m-%d") -> bool:
    """Validate that date range is logical"""
    try:
        start = datetime.strptime(start_date, date_format).date()
        end = datetime.strptime(end_date, date_format).date()
        return start <= end
    except ValueError:
        return False


def is_business_day(check_date: date) -> bool:
    """Check if a date is a business day (Monday-Friday)"""
    return check_date.weekday() < 5


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    if not filename:
        return "untitled"
    
    # Remove path separators and other dangerous characters
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
    
    # Truncate if too long
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        if ext:
            max_name_length = 255 - len(ext) - 1
            sanitized = name[:max_name_length] + '.' + ext
        else:
            sanitized = sanitized[:255]
    
    return sanitized or "untitled"


def validate_positive_number(value: str) -> bool:
    """Validate that a string represents a positive number"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_integer_range(value: str, min_val: int = None, max_val: int = None) -> bool:
    """Validate that a string is an integer within specified range"""
    try:
        num = int(value)
        
        if min_val is not None and num < min_val:
            return False
        
        if max_val is not None and num > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def is_safe_string(text: str, max_length: int = 1000) -> bool:
    """Check if string is safe (no potentially dangerous content)"""
    if not text:
        return True
    
    if len(text) > max_length:
        return False
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript URLs
        r'data:text/html',           # Data URLs with HTML
        r'on\w+\s*=',                # Event handlers
        r'SELECT.*FROM|INSERT.*INTO|UPDATE.*SET|DELETE.*FROM',  # SQL
        r'UNION.*SELECT|DROP.*TABLE', # More SQL
        r'<%.*%>',                   # Server-side includes
        r'\$\{.*\}',                 # Template injection
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
            return False
    
    return True


def normalize_ticker(ticker: str) -> str:
    """Normalize ticker symbol to standard format"""
    if not ticker:
        return ""
    
    return ticker.strip().upper()


def normalize_cik(cik: str) -> str:
    """Normalize CIK to 10-digit format with leading zeros"""
    if not cik:
        return ""
    
    # Extract only digits
    digits_only = ''.join(filter(str.isdigit, cik))
    
    # Pad with leading zeros to make 10 digits
    return digits_only.zfill(10) if digits_only else ""


def validate_json_structure(data: dict, required_fields: list) -> tuple[bool, list]:
    """Validate that JSON data contains required fields"""
    missing_fields = []
    
    for field in required_fields:
        if '.' in field:
            # Handle nested fields
            keys = field.split('.')
            current = data
            
            try:
                for key in keys:
                    if not isinstance(current, dict) or key not in current:
                        missing_fields.append(field)
                        break
                    current = current[key]
            except (TypeError, KeyError):
                missing_fields.append(field)
        else:
            # Handle top-level fields
            if field not in data:
                missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def is_valid_iso_date(date_str: str) -> bool:
    """Validate ISO format date string (YYYY-MM-DD)"""
    return is_valid_date(date_str, "%Y-%m-%d")


def is_valid_currency_code(currency: str) -> bool:
    """Validate 3-letter currency code"""
    if not currency or len(currency) != 3:
        return False
    
    # Common currency codes
    valid_currencies = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 
        'SEK', 'NZD', 'MXN', 'SGD', 'HKD', 'NOK', 'TRY', 'ZAR',
        'BRL', 'INR', 'KRW', 'RUB'
    }
    
    return currency.upper() in valid_currencies


def validate_percentage(value: str) -> bool:
    """Validate percentage value (-100 to 100)"""
    try:
        num = float(value)
        return -100 <= num <= 100
    except (ValueError, TypeError):
        return False


def is_alphanumeric_with_spaces(text: str) -> bool:
    """Check if text contains only alphanumeric characters and spaces"""
    if not text:
        return True
    
    return all(c.isalnum() or c.isspace() for c in text)


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validate file extension against allowed list"""
    if not filename or not allowed_extensions:
        return False
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_ext in [ext.lower().lstrip('.') for ext in allowed_extensions]