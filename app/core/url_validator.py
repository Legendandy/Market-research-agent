"""
URL validation and normalization utilities
"""
import re
from urllib.parse import urlparse
from typing import Optional

def normalize_url(url: str) -> Optional[str]:
    """
    Normalize URL to ensure it has proper protocol and format.
    
    Accepts:
    - https://github.com
    - http://github.com
    - www.github.com
    - github.com
    
    Args:
        url: URL string in various formats
        
    Returns:
        Normalized URL with https:// protocol or None if invalid
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # Remove any leading/trailing whitespace or quotes
    url = url.strip('\'"')
    
    # If no protocol, add https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse and validate
    try:
        parsed = urlparse(url)
        
        # Must have a valid scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return None
        
        # Ensure scheme is http or https
        if parsed.scheme not in ['http', 'https']:
            return None
        
        # Basic domain validation (must have at least one dot or be localhost)
        netloc = parsed.netloc.lower()
        if netloc == 'localhost' or '.' in netloc:
            return url
        
        return None
        
    except Exception:
        return None


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.
    
    Args:
        url: URL string
        
    Returns:
        True if valid, False otherwise
    """
    return normalize_url(url) is not None


def extract_company_name(url: str) -> str:
    """
    Extract company name from URL.
    
    Args:
        url: Company website URL
        
    Returns:
        Cleaned company name
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        
        # Extract main domain name (before first dot)
        match = re.match(r'^([^.]+)', domain)
        if match:
            name = match.group(1)
            # Format: capitalize and replace hyphens
            name = name.replace('-', ' ').replace('_', ' ')
            return name.title()
        
        return domain.title()
        
    except Exception:
        return url


def extract_domain(url: str) -> str:
    """
    Extract clean domain from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain without protocol or path
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
    except Exception:
        return url