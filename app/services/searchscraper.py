"""
SearchScraper Service
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
    """SearchScraper wrapper service"""
    
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
    
    def search_competitors(self, company_overview: str) -> str:
        """
        Fetch and analyze competitor data.
        
        Args:
            company_overview: Company overview text from SmartCrawler
            
        Returns:
            Structured competitor analysis
        """
        try:
            # Extract company name
            company_name = self._extract_company_name(company_overview)
            logger.info(f"[SearchScraper] Company name: '{company_name}'")
            
            # Create targeted queries
            queries = [
                f"{company_name} competitors direct rivals",
                f"{company_name} alternative similar companies",
            ]
            
            all_results = []
            
            # Run multiple queries
            for query in queries:
                try:
                    raw_resp = self._search_request(query, num_results=5)
                    if raw_resp and raw_resp.get("result"):
                        all_results.append(raw_resp["result"])
                except Exception as query_error:
                    logger.warning(f"[SearchScraper] Query failed: {query_error}")
                    continue
            
            if not all_results:
                return "❌ No competitor data found. Try providing more context about the company."
            
            # Process results
            combined_data = self._combine_search_results(all_results)
            
            # Limit data size
            if len(combined_data) > settings.MAX_SEARCH_DATA_LENGTH:
                combined_data = combined_data[:settings.MAX_SEARCH_DATA_LENGTH] + "\n\n[Data truncated due to length]"
            
            # Generate analysis
            return self._generate_competitor_analysis(company_overview, combined_data)
            
        except Exception as e:
            logger.error(f"[SearchScraper] Failed: {e}", exc_info=True)
            return f"❌ Error fetching competitor data: {str(e)}\n\nPlease try again."
    
    def _extract_company_name(self, overview: str) -> str:
        """Extract company name from overview"""
        overview_lines = overview.split('\n')
        first_line = overview_lines[0] if overview_lines else overview
        
        # Take first 5 words
        company_name_match = first_line.split()[:5]
        company_name = " ".join(company_name_match)
        
        # Remove common words
        company_name = re.sub(r'\b(the|a|an|is|are|was|were)\b', '', company_name, flags=re.IGNORECASE)
        return company_name.strip()
    
    def _combine_search_results(self, results: list) -> str:
        """Combine search results into structured format"""
        combined_results = []
        
        for result in results:
            if isinstance(result, dict):
                if "companies" in result and result["companies"]:
                    companies_text = []
                    for company in result["companies"]:
                        if isinstance(company, dict):
                            name = company.get("name", "Unknown")
                            desc = company.get("description", "No description")
                            companies_text.append(f"**{name}**: {desc}")
                        else:
                            companies_text.append(str(company))
                    combined_results.append("\n".join(companies_text))
                else:
                    combined_results.append(str(result))
            else:
                combined_results.append(str(result))
        
        return "\n\n---\n\n".join(combined_results)
    
    def _generate_competitor_analysis(self, company_overview: str, search_data: str) -> str:
        """Generate structured competitor analysis using LLM"""
        prompt = (
            "You are an expert competitive intelligence analyst.\n\n"
            "MISSION: Analyze the search data and identify the most direct, relevant competitors.\n\n"
            "OUTPUT FORMAT:\n\n"
            "# 🏢 Direct Competitors Analysis\n\n"
            "## [Company Name 1]\n"
            "**🎯 Core Focus:** [What they do - concise]\n"
            "**💰 Business Model:** [Revenue model]\n"
            "**📊 Market Position:** [Leader/Challenger/Niche]\n"
            "**🏢 Company Size:** [Stage + rough employee count]\n"
            "**💵 Funding/Revenue:** [Latest financial data if available]\n"
            "**🎯 Target Market:** [Primary customer segments]\n"
            "**⚡ Key Differentiator:** [Main competitive advantage]\n"
            "**🌍 Geographic Reach:** [Primary markets]\n\n"
            "REQUIREMENTS:\n"
            "- Include 4-6 most relevant competitors\n"
            "- Keep descriptions concise (max 15 words per bullet)\n"
            "- Skip indirect/tangential competitors\n"
            "- Use 'Not available' only if truly no data\n"
            "- Focus on direct competitors in the same space\n\n"
            f"COMPANY ANALYZED:\n{company_overview[:500]}\n\n"
            f"SEARCH DATA:\n{search_data}"
        )
        
        result = llm_service.invoke(prompt)
        
        # Ensure result is string
        if isinstance(result, list):
            result = "\n".join(str(item) for item in result)
        else:
            result = str(result) if result else ""
        
        # Validation
        if not result or len(result) < 100:
            return "❌ Unable to extract meaningful competitor data.\n\n**Suggestion:** The search results may not contain competitor information."
        
        # Clean up formatting
        if "# 🏢 Direct Competitors Analysis" not in result:
            result = "# 🏢 Direct Competitors Analysis\n\n" + result
        
        return result

# Singleton instance
searchscraper_service = SearchScraperService()