"""
SearchScraper Service - Enhanced with multi-source queries
Modified: URL-only company name extraction
"""
import re
import logging
from http.client import RemoteDisconnected
from tenacity import retry, stop_after_attempt, wait_exponential
from scrapegraph_py import Client
from app.config import settings
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class SearchScraperService:
    """SearchScraper wrapper service with enhanced data collection"""
    
    def __init__(self):
        """Initialize SearchScraper client"""
        self.client = Client(api_key=settings.SMARTCRAWLER_API_KEY)
        logger.info("✅ SearchScraper Service initialized")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _search_request(self, query: str, num_results: int = 5) -> dict:
        """Execute SearchScraper query with retry logic"""
        try:
            logger.info(f"[SearchScraper] Searching: {query}")
            resp = self.client.searchscraper(user_prompt=query, num_results=num_results)
            logger.info("[SearchScraper] ✅ Search completed")
            return resp
        except RemoteDisconnected:
            logger.warning("[SearchScraper] RemoteDisconnected, retrying...")
            raise
        except Exception as e:
            logger.error(f"[SearchScraper] Exception: {e}")
            raise
    
    def search_competitors(self, company_overview: str, company_url: str) -> str:
        """
        Fetch and analyze competitor data.
        
        Args:
            company_overview: Company overview text from SmartCrawler
            company_url: Original company URL (REQUIRED for extraction)
            
        Returns:
            Structured competitor analysis
        """
        try:
            # Extract company name from URL ONLY
            if not company_url:
                return "❌ Company URL is required for competitor search. Please provide a valid URL."
            
            company_name = self._extract_from_url(company_url)
            logger.info(f"[SearchScraper] Extracted company name from URL: '{company_name}'")
            
            if not company_name or len(company_name) < 2:
                return f"❌ Unable to extract company name from URL: {company_url}"
            
            # ENHANCED: Multiple targeted queries for better results
            queries = [
                f"{company_name} competitors direct rivals",
                f"{company_name} vs alternative similar companies",
                 f"{company_name} founders CEO leadership team and funding investors valuation ",
                f"{company_name} revenue business model, market size industry TAM, SAM, and SOM",
                f"{company_name} company history and founders",
            ]
            
            all_results = []
            
            # Run multiple queries
            for query in queries:
                try:
                    raw_resp = self._search_request(query, num_results=5)
                    if raw_resp and raw_resp.get("result"):
                        all_results.append(raw_resp["result"])
                except Exception as query_error:
                    logger.warning(f"[SearchScraper] Query '{query}' failed: {query_error}")
                    continue
            
            if not all_results:
                return "❌ No competitor data found. The company may be very new or have limited online presence."
            
            # Process results
            combined_data = self._combine_search_results(all_results)
            
            # Limit data size
            if len(combined_data) > settings.MAX_SEARCH_DATA_LENGTH:
                combined_data = combined_data[:settings.MAX_SEARCH_DATA_LENGTH] + "\n\n[Data truncated due to length]"
            
            # Generate analysis
            return self._generate_competitor_analysis(company_name, company_overview, combined_data)
            
        except Exception as e:
            logger.error(f"[SearchScraper] Failed: {e}", exc_info=True)
            return f"❌ Error fetching competitor data: {str(e)}\n\nPlease try again."
    
    def search_company_intelligence(self, company_name: str, company_url: str = None) -> str:
        """
        NEW: Search for additional company intelligence not found on website.
        This supplements SmartCrawler data with external sources.
        
        Args:
            company_name: Company name (extracted from URL if provided)
            company_url: Company URL (used for extraction if provided)
            
        Returns:
            Additional company intelligence (founders, funding, news, etc.)
        """
        try:
            # If URL provided, extract company name from it
            if company_url:
                company_name = self._extract_from_url(company_url)
                logger.info(f"[SearchScraper] Using URL-extracted name: {company_name}")
            
            if not company_name:
                return "❌ Company name or URL required for intelligence search."
            
            logger.info(f"[SearchScraper] Searching intelligence for: {company_name}")
            
            # ENHANCED: Specific queries for missing information
            intelligence_queries = [
                f"{company_name} founders CEO leadership team",
                f"{company_name} funding investors valuation",
                f"{company_name} revenue business model",
                f"{company_name} company history founded",
                f"{company_name} latest news announcements 2024 2025",
                f"{company_name} market size industry TAM",
            ]
            
            all_intelligence = []
            
            for query in intelligence_queries:
                try:
                    raw_resp = self._search_request(query, num_results=3)
                    if raw_resp and raw_resp.get("result"):
                        all_intelligence.append({
                            "query": query,
                            "data": raw_resp["result"]
                        })
                except Exception as query_error:
                    logger.warning(f"[SearchScraper] Intelligence query failed: {query_error}")
                    continue
            
            if not all_intelligence:
                return "❌ No additional intelligence found."
            
            # Format intelligence data
            formatted_intelligence = self._format_intelligence(all_intelligence)
            
            return formatted_intelligence
            
        except Exception as e:
            logger.error(f"[SearchScraper] Intelligence search failed: {e}", exc_info=True)
            return f"❌ Error fetching company intelligence: {str(e)}"
    
    def _format_intelligence(self, intelligence_data: list) -> str:
        """Format intelligence data into structured sections"""
        sections = {}
        
        for item in intelligence_data:
            query = item["query"]
            data = item["data"]
            
            # Categorize by query type
            if "founder" in query.lower() or "ceo" in query.lower() or "leadership" in query.lower():
                sections.setdefault("Leadership & Founders", []).append(data)
            elif "funding" in query.lower() or "investor" in query.lower():
                sections.setdefault("Funding & Investors", []).append(data)
            elif "revenue" in query.lower() or "business model" in query.lower():
                sections.setdefault("Revenue & Business Model", []).append(data)
            elif "history" in query.lower() or "founded" in query.lower():
                sections.setdefault("Company History", []).append(data)
            elif "news" in query.lower() or "announcement" in query.lower():
                sections.setdefault("Recent News", []).append(data)
            elif "market" in query.lower() or "tam" in query.lower():
                sections.setdefault("Market Intelligence", []).append(data)
        
        # Build formatted output
        output = "# 🔍 External Intelligence Data\n\n"
        
        for section, data_list in sections.items():
            output += f"## {section}\n\n"
            for data in data_list:
                output += f"{self._stringify_data(data)}\n\n---\n\n"
        
        return output
    
    def _stringify_data(self, data) -> str:
        """Convert data to readable string"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
    
    def _extract_from_url(self, url: str) -> str:
        """
        Extract company name from URL domain.
        MODIFIED: Returns full domain (e.g., 'github.com', 'google.com') for common platforms.
        """
        try:
            # Extract domain from URL
            domain_match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})', url)
            if not domain_match:
                # Try simpler pattern for just domain.tld
                domain_match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', url)
            
            if domain_match:
                full_domain = domain_match.group(1)
                logger.info(f"[URL Extraction] Full domain: '{full_domain}'")
                
                # List of common platforms where we use the full domain
                common_platforms = [
                    'github.com', 'google.com', 'facebook.com', 'twitter.com', 
                    'linkedin.com', 'youtube.com', 'instagram.com', 'reddit.com',
                    'amazon.com', 'microsoft.com', 'apple.com', 'meta.com',
                    'tiktok.com', 'snapchat.com', 'pinterest.com', 'netflix.com'
                ]
                
                # Check if it's a common platform
                for platform in common_platforms:
                    if full_domain.lower().endswith(platform.lower()):
                        logger.info(f"[URL Extraction] Detected common platform, using full domain: '{full_domain}'")
                        return full_domain
                
                # For other domains, extract just the main part
                # e.g., "example.co.uk" -> "example", "mycompany.com" -> "mycompany"
                main_domain = full_domain.split('.')[0]
                formatted_name = self._format_domain_name(main_domain)
                logger.info(f"[URL Extraction] Using formatted name: '{formatted_name}'")
                return formatted_name
            
            logger.warning(f"[URL Extraction] Could not extract domain from: {url}")
            return ""
            
        except Exception as e:
            logger.error(f"URL extraction error: {e}")
            return ""
    
    def _format_domain_name(self, domain: str) -> str:
        """Format domain name into company name"""
        # Known brand capitalizations
        known_formats = {
            'github': 'GitHub', 'gitlab': 'GitLab', 'linkedin': 'LinkedIn',
            'youtube': 'YouTube', 'airbnb': 'Airbnb', 'shopify': 'Shopify',
            'stripe': 'Stripe', 'mongodb': 'MongoDB', 'postgresql': 'PostgreSQL',
            'facebook': 'Facebook', 'google': 'Google', 'microsoft': 'Microsoft',
            'apple': 'Apple', 'amazon': 'Amazon', 'netflix': 'Netflix',
            'twitter': 'Twitter', 'instagram': 'Instagram', 'tiktok': 'TikTok',
            'snapchat': 'Snapchat', 'pinterest': 'Pinterest', 'reddit': 'Reddit'
        }
        
        domain_lower = domain.lower()
        if domain_lower in known_formats:
            return known_formats[domain_lower]
        
        # Format generic domains: replace hyphens/underscores with spaces, title case
        return domain.replace('-', ' ').replace('_', ' ').title()
    
    def _combine_search_results(self, results: list) -> str:
        """Combine search results"""
        combined = []
        for result in results:
            if isinstance(result, dict):
                if "companies" in result and result["companies"]:
                    for company in result["companies"]:
                        if isinstance(company, dict):
                            name = company.get("name", "Unknown")
                            desc = company.get("description", "No description")
                            combined.append(f"**{name}**: {desc}")
                        else:
                            combined.append(str(company))
                else:
                    combined.append(str(result))
            else:
                combined.append(str(result))
        
        return "\n\n---\n\n".join(combined)
    
    def _generate_competitor_analysis(self, company_name: str, company_overview: str, search_data: str) -> str:
        """Generate structured competitor analysis"""
        prompt = f"""You are an expert competitive intelligence analyst.

COMPANY ANALYZED: {company_name}

MISSION: Analyze search data and identify 5-7 most direct, relevant competitors with detailed information.

OUTPUT FORMAT:

# 🏢 Competitive Intelligence Report

## [Competitor 1 Name]
**🎯 Core Business:** [What they do - 1 sentence]
**💰 Business Model:** [How they make money]
**📊 Market Position:** [Leader/Challenger/Niche Player]
**🏢 Company Size:** [Employee count/funding stage]
**💵 Funding/Revenue:** [Latest data with sources]
**🎯 Target Market:** [Primary customer segments]
**⚡ Key Differentiator:** [Main competitive advantage vs {company_name}]
**🌍 Geographic Reach:** [Markets served]
**📈 Recent News:** [Latest developments, if available]

REQUIREMENTS:
- Include 5-7 most relevant direct competitors
- Prioritize competitors in the same market/industry
- Keep each bullet point under 20 words
- Include specific numbers (funding, revenue, users) when available
- Skip indirect/tangential competitors
- If data not available, write "Not disclosed"
- Compare each competitor to {company_name}

COMPANY CONTEXT:
{company_overview[:500]}

SEARCH DATA:
{search_data}

Provide detailed competitor analysis:"""
        
        result = llm_service.invoke(prompt)
        
        if isinstance(result, list):
            result = "\n".join(str(item) for item in result)
        else:
            result = str(result) if result else ""
        
        if not result or len(result) < 100:
            return "❌ Unable to extract meaningful competitor data.\n\n**Suggestion:** Try searching manually or provide more context."
        
        if "# 🏢" not in result:
            result = "# 🏢 Competitive Intelligence Report\n\n" + result
        
        return result

# Singleton instance
searchscraper_service = SearchScraperService()