"""
Natural Language Query Parser for Smart GTM Agent
Extracts URLs and analysis types from conversational prompts
"""
import re
from typing import Tuple, Optional
from urllib.parse import urlparse

class QueryParser:
    """Parse natural language queries to extract URLs and analysis types"""
    
    # Analysis type keywords and their mappings
    ANALYSIS_KEYWORDS = {
        'research': ['research', 'analyze', 'analysis', 'study', 'investigate', 'intel', 'intelligence'],
        'go-to-market': ['go-to-market', 'gtm', 'go to market', 'market strategy', 'launch', 'strategy'],
        'channel': ['channel', 'distribution', 'channels', 'sales channel', 'marketing channel']
    }
    
    @classmethod
    def parse(cls, query: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse natural language query to extract URL and analysis type.
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (raw_url, analysis_type, error_message)
            - raw_url: Extracted URL or None
            - analysis_type: 'research', 'go-to-market', 'channel', or None
            - error_message: Error message if parsing failed, or None
        """
        if not query or not isinstance(query, str):
            return None, None, "❌ Empty query received. Please provide a valid request."
        
        query = query.strip()
        
        # Check if it's the legacy pipe format: "url | type"
        if '|' in query:
            return cls._parse_legacy_format(query)
        
        # Extract URL from natural language
        url = cls._extract_url(query)
        
        # Extract analysis type from natural language
        analysis_type = cls._extract_analysis_type(query)
        
        # Validation
        if not url:
            return None, None, cls._generate_help_message("no_url")
        
        if not analysis_type:
            return url, 'research', None
        
        return url, analysis_type, None
    
    @classmethod
    def _parse_legacy_format(cls, query: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parse legacy pipe-separated format: 'url | type'"""
        parts = query.split('|')
        
        if len(parts) != 2:
            return None, None, cls._generate_help_message("invalid_format")
        
        raw_url = parts[0].strip()
        analysis_type = parts[1].strip().lower()
        
        # Validate URL exists
        if not raw_url:
            return None, None, cls._generate_help_message("no_url")
        
        # Validate analysis type
        valid_types = ['research', 'go-to-market', 'channel']
        if analysis_type not in valid_types:
            return raw_url, None, cls._generate_help_message("invalid_type", analysis_type)
        
        return raw_url, analysis_type, None
    
    @classmethod
    def _extract_url(cls, text: str) -> Optional[str]:
        """
        Extract URL from text using multiple patterns.
        
        Patterns supported:
        - https://example.com
        - http://example.com
        - www.example.com
        - example.com
        - example.co.uk
        """
        # Pattern 1: URLs with protocol
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        
        # Pattern 2: www.domain.com
        www_pattern = r'\bwww\.[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?\b'
        match = re.search(www_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        
        # Pattern 3: domain.com (more conservative to avoid false positives)
        # Must have at least one letter before the TLD
        domain_pattern = r'\b[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?\b'
        
        # Find all potential domains
        potential_domains = re.findall(domain_pattern, text, re.IGNORECASE)
        
        # Filter out common false positives (file extensions, etc.)
        excluded_tlds = ['jpg', 'png', 'gif', 'pdf', 'doc', 'txt', 'csv', 'json', 'xml']
        
        for domain in potential_domains:
            tld = domain.split('.')[-1].lower()
            if tld not in excluded_tlds:
                return domain
        
        return None
    
    @classmethod
    def _extract_analysis_type(cls, text: str) -> Optional[str]:
        """
        Extract analysis type from text based on keywords.
        
        Returns:
            'research', 'go-to-market', 'channel', or None
        """
        text_lower = text.lower()
        
        # Check each analysis type's keywords
        for analysis_type, keywords in cls.ANALYSIS_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    return analysis_type
        
        # Default to 'research' if URL found but no type specified
        # (This will be caught by validation and show help message)
        return None
    
    @classmethod
    def _generate_help_message(cls, error_type: str, extra_info: str = None) -> str:
        """Generate helpful error messages based on error type"""
        
        if error_type == "no_url":
            return (
                "❌ **No URL detected in your request.**\n\n"
                "**I need a company website URL to analyze.** Please try again with:\n\n"
                "**Examples:**\n"
                "• \"Give me a channel analysis for example.com\"\n"
                "• \"I need go-to-market strategy for https://github.com\"\n"
                "• \"Research shopify.com for me\"\n"
                "• \"example.com | research\" *(classic format)*\n\n"
                "**Supported formats:**\n"
                "✅ https://example.com\n"
                "✅ www.example.com\n"
                "✅ example.com\n\n"
                "**Analysis types available:**\n"
                "🔍 **research** - Company overview, competitors, market insights\n"
                "🚀 **go-to-market** - GTM strategy, pricing, distribution\n"
                "📢 **channel** - Distribution channels, partnerships, economics"
            )
        
        elif error_type == "no_type":
            return (
                "❌ **No analysis type detected in your request.**\n\n"
                "**Please specify what type of analysis you need:**\n\n"
                "**Examples:**\n"
                "• \"Give me a **channel** analysis for example.com\"\n"
                "• \"I need **go-to-market** strategy for example.com\"\n"
                "• \"Do **research** on example.com\"\n\n"
                "**Available analysis types:**\n"
                "🔍 **research** - Company overview, founders, funding, competitors, market trends\n"
                "🚀 **go-to-market** - GTM strategy, ICP, messaging, pricing, sales channels\n"
                "📢 **channel** - Distribution strategy, partnerships, channel economics, roadmap\n\n"
                "**Keywords I understand:**\n"
                "• Research: research, analyze, study, investigate\n"
                "• Go-to-Market: gtm, go-to-market, market strategy, launch\n"
                "• Channel: channel, distribution, sales channel"
            )
        
        elif error_type == "invalid_type":
            return (
                f"❌ **Invalid analysis type: '{extra_info}'**\n\n"
                "**Please use one of these valid types:**\n\n"
                "🔍 **research** - Company overview, competitors, market insights\n"
                "🚀 **go-to-market** - GTM strategy, pricing, distribution\n"
                "📢 **channel** - Distribution channels, partnerships, economics\n\n"
                "**Examples:**\n"
                "• \"example.com | research\"\n"
                "• \"example.com | go-to-market\"\n"
                "• \"example.com | channel\""
            )
        
        elif error_type == "invalid_format":
            return (
                "❌ **Invalid format detected.**\n\n"
                "**I support two formats:**\n\n"
                "**1. Natural Language** *(Recommended)*\n"
                "• \"Give me channel analysis for example.com\"\n"
                "• \"I need go-to-market strategy for github.com\"\n"
                "• \"Research shopify.com\"\n\n"
                "**2. Classic Format**\n"
                "• \"example.com | research\"\n"
                "• \"example.com | go-to-market\"\n"
                "• \"example.com | channel\"\n\n"
                "**Analysis types:**\n"
                "🔍 research 🚀 go-to-market 📢 channel"
            )
        
        return "❌ Unable to parse your request. Please provide a URL and analysis type."


# Convenience function for quick parsing
def parse_query(query: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Quick parse function.
    
    Returns:
        (url, analysis_type, error_message)
    """
    return QueryParser.parse(query)