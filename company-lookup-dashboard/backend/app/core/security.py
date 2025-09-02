import re
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from fastapi import Request, HTTPException
from app.config import settings
from app.core.exceptions import RateLimitExceededError, ValidationError

logger = logging.getLogger(__name__)


class SecurityService:
    """Security service for rate limiting, validation, and sanitization"""
    
    def __init__(self):
        # In-memory storage for rate limiting (in production, use Redis)
        self._rate_limit_store: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Validation patterns
        self.ticker_pattern = re.compile(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$')
        self.cik_pattern = re.compile(r'^\d{1,10}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Suspicious patterns to detect potential attacks
        self.suspicious_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'SELECT.*FROM|INSERT.*INTO|UPDATE.*SET|DELETE.*FROM', re.IGNORECASE),
            re.compile(r'UNION.*SELECT|DROP.*TABLE', re.IGNORECASE)
        ]
        
        # Allowed file extensions for uploads (if implemented)
        self.allowed_extensions = {'.pdf', '.txt', '.csv', '.json'}
    
    def get_client_id(self, request: Request) -> str:
        """Get unique client identifier for rate limiting"""
        # Try to get real IP from headers (in case behind proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else 'unknown'
        
        # Include user agent for better uniqueness
        user_agent = request.headers.get('User-Agent', '')
        user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
        
        return f"{client_ip}:{user_agent_hash}"
    
    def check_rate_limit(self, request: Request, limit_per_minute: int = None, limit_per_hour: int = None) -> None:
        """Check if request is within rate limits"""
        client_id = self.get_client_id(request)
        now = datetime.utcnow()
        
        # Use configured limits if not provided
        limit_per_minute = limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        limit_per_hour = limit_per_hour or settings.RATE_LIMIT_PER_HOUR
        
        # Get or create client record
        if client_id not in self._rate_limit_store:
            self._rate_limit_store[client_id] = {
                'requests': [],
                'blocked_until': None
            }
        
        client_data = self._rate_limit_store[client_id]
        
        # Check if client is temporarily blocked
        if client_data.get('blocked_until') and now < client_data['blocked_until']:
            retry_after = int((client_data['blocked_until'] - now).total_seconds())
            raise RateLimitExceededError(
                f"Rate limit exceeded. Try again in {retry_after} seconds",
                retry_after=retry_after
            )
        
        # Clean old requests (older than 1 hour)
        one_hour_ago = now - timedelta(hours=1)
        client_data['requests'] = [
            req_time for req_time in client_data['requests'] 
            if req_time > one_hour_ago
        ]
        
        # Count recent requests
        one_minute_ago = now - timedelta(minutes=1)
        requests_last_minute = len([
            req_time for req_time in client_data['requests'] 
            if req_time > one_minute_ago
        ])
        requests_last_hour = len(client_data['requests'])
        
        # Check minute limit
        if requests_last_minute >= limit_per_minute:
            # Block for 1 minute
            client_data['blocked_until'] = now + timedelta(minutes=1)
            raise RateLimitExceededError(
                f"Rate limit exceeded: {limit_per_minute} requests per minute",
                retry_after=60
            )
        
        # Check hour limit
        if requests_last_hour >= limit_per_hour:
            # Block for remaining time in hour
            client_data['blocked_until'] = now + timedelta(minutes=60)
            raise RateLimitExceededError(
                f"Rate limit exceeded: {limit_per_hour} requests per hour",
                retry_after=3600
            )
        
        # Record this request
        client_data['requests'].append(now)
        
        logger.debug(f"Rate limit check passed for {client_id}: {requests_last_minute}/min, {requests_last_hour}/hour")
    
    def validate_ticker(self, ticker: str) -> str:
        """Validate and normalize stock ticker symbol"""
        if not ticker:
            raise ValidationError("Ticker symbol is required", field="ticker")
        
        ticker = ticker.strip().upper()
        
        if not self.ticker_pattern.match(ticker):
            raise ValidationError(
                "Invalid ticker format. Must be 1-5 uppercase letters, optionally followed by a dot and 1-2 letters",
                field="ticker",
                value=ticker
            )
        
        return ticker
    
    def validate_cik(self, cik: str) -> str:
        """Validate and normalize SEC CIK"""
        if not cik:
            raise ValidationError("CIK is required", field="cik")
        
        # Remove any non-digit characters
        cik_digits = ''.join(filter(str.isdigit, cik))
        
        if not cik_digits or not self.cik_pattern.match(cik_digits):
            raise ValidationError(
                "Invalid CIK format. Must be 1-10 digits",
                field="cik", 
                value=cik
            )
        
        # Pad with leading zeros to make 10 digits
        return cik_digits.zfill(10)
    
    def validate_search_query(self, query: str) -> str:
        """Validate and sanitize search query"""
        if not query:
            raise ValidationError("Search query is required", field="query")
        
        query = query.strip()
        
        # Check minimum length
        if len(query) < settings.MIN_SEARCH_QUERY_LENGTH:
            raise ValidationError(
                f"Search query must be at least {settings.MIN_SEARCH_QUERY_LENGTH} characters",
                field="query",
                value=query
            )
        
        # Check maximum length
        if len(query) > 100:
            raise ValidationError(
                "Search query too long (max 100 characters)",
                field="query",
                value=query
            )
        
        # Sanitize query
        sanitized_query = self.sanitize_input(query)
        
        return sanitized_query
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not input_str:
            return input_str
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern.search(input_str):
                logger.warning(f"Suspicious input detected: {input_str}")
                raise ValidationError(
                    "Input contains potentially malicious content",
                    field="input",
                    value=input_str
                )
        
        # Basic HTML encoding for safety
        sanitized = (input_str
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        
        return sanitized
    
    def validate_email(self, email: str) -> str:
        """Validate email format"""
        if not email:
            raise ValidationError("Email is required", field="email")
        
        email = email.strip().lower()
        
        if not self.email_pattern.match(email):
            raise ValidationError(
                "Invalid email format",
                field="email",
                value=email
            )
        
        return email
    
    def validate_date_range(self, date_from: str = None, date_to: str = None) -> tuple:
        """Validate date range inputs"""
        parsed_from = None
        parsed_to = None
        
        if date_from:
            try:
                parsed_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(
                    "Invalid date format. Use YYYY-MM-DD",
                    field="date_from",
                    value=date_from
                )
        
        if date_to:
            try:
                parsed_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(
                    "Invalid date format. Use YYYY-MM-DD", 
                    field="date_to",
                    value=date_to
                )
        
        # Validate date range logic
        if parsed_from and parsed_to and parsed_from > parsed_to:
            raise ValidationError(
                "Start date cannot be after end date",
                field="date_range"
            )
        
        # Check if dates are reasonable (not too far in the past/future)
        today = datetime.utcnow().date()
        min_date = datetime(1990, 1, 1).date()  # SEC data generally starts from 1990s
        max_date = today + timedelta(days=365)  # Allow up to 1 year in future
        
        if parsed_from and (parsed_from < min_date or parsed_from > max_date):
            raise ValidationError(
                f"Start date must be between {min_date} and {max_date}",
                field="date_from",
                value=date_from
            )
        
        if parsed_to and (parsed_to < min_date or parsed_to > max_date):
            raise ValidationError(
                f"End date must be between {min_date} and {max_date}",
                field="date_to", 
                value=date_to
            )
        
        return parsed_from, parsed_to
    
    def generate_request_id(self, request: Request) -> str:
        """Generate unique request ID for tracking"""
        timestamp = str(int(datetime.utcnow().timestamp() * 1000))
        client_id = self.get_client_id(request)
        path_hash = hashlib.md5(str(request.url.path).encode()).hexdigest()[:8]
        
        return f"req_{timestamp}_{path_hash}_{client_id.replace(':', '_')}"
    
    def log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request for monitoring"""
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else 'unknown',
                "user_agent": request.headers.get('User-Agent', ''),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def cleanup_rate_limit_store(self):
        """Clean up old entries from rate limit store"""
        cutoff_time = datetime.utcnow() - timedelta(hours=2)
        
        clients_to_remove = []
        for client_id, client_data in self._rate_limit_store.items():
            # Remove old requests
            client_data['requests'] = [
                req_time for req_time in client_data['requests'] 
                if req_time > cutoff_time
            ]
            
            # Remove clients with no recent activity
            if not client_data['requests'] and (
                not client_data.get('blocked_until') or 
                client_data['blocked_until'] < datetime.utcnow()
            ):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self._rate_limit_store[client_id]
        
        if clients_to_remove:
            logger.info(f"Cleaned up {len(clients_to_remove)} inactive rate limit entries")


# Global security service instance
security_service = SecurityService()