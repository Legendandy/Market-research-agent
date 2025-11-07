"""
SearchScraper Service - FIXED based on working code
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
        """
        Execute SearchScraper query with retry logic.
        Based on working code - returns immediate results, no polling needed.
        """
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
            # Extract company name from overview
            company_name = self._extract_company_name(company_overview)
            logger.info(f"[SearchScraper] Analyzing competitors for: '{company_name}'")
            
            # Create targeted queries (matching working code pattern)
            queries = [
                f"{company_name} competitors direct rivals and similar companies",
                f"{company_name} vs competitors comparison market",
            ]
            
            all_results = []
            
            # Run multiple queries
            for query in queries:
                try:
                    raw_resp = self._search_request(query, num_results=5)
                    
                    # Extract result from response
                    if raw_resp and raw_resp.get("result"):
                        all_results.append(raw_resp["result"])
                        logger.info(f"[SearchScraper] ✅ Query successful")
                    else:
                        logger.warning(f"[SearchScraper] No result for query")
                        
                except Exception as query_error:
                    logger.warning(f"[SearchScraper] Query failed: {query_error}")
                    continue
            
            if not all_results:
                return (
                    "❌ No competitor data found.\n\n"
                    "**Possible reasons:**\n"
                    "- Company name unclear from overview\n"
                    "- No public competitor information available\n\n"
                    "**Suggestion:** Provide more context or try a different URL."
                )
            
            # Process results
            combined_data = self._combine_search_results(all_results)
            
            # Limit data size
            if len(combined_data) > settings.MAX_SEARCH_DATA_LENGTH:
                combined_data = combined_data[:settings.MAX_SEARCH_DATA_LENGTH] + "\n\n[Data truncated]"
            
            # Generate analysis
            return self._generate_competitor_analysis(company_overview, combined_data)
            
        except Exception as e:
            logger.error(f"[SearchScraper] Failed: {e}", exc_info=True)
            return (
                f"❌ Error fetching competitor data: {str(e)}\n\n"
                "Please try again or check if the service is available."
            )
    
    def _extract_company_name(self, overview: str) -> str:
        """Extract company name from overview (matching working code)"""
        # Take first few words as likely company name
        overview_lines = overview.split('\n')
        first_line = overview_lines[0] if overview_lines else overview
        
        # Take first 3-5 words
        company_name_match = first_line.split()[:5]
        company_name = " ".join(company_name_match)
        
        # Remove common words
        company_name = re.sub(
            r'\b(the|a|an|is|are|was|were|company|inc|ltd|llc)\b', 
            '', 
            company_name, 
            flags=re.IGNORECASE
        )
        return company_name.strip()
    
    def _combine_search_results(self, results: list) -> str:
        """Combine search results into structured format (matching working code)"""
        combined_results = []
        
        for result in results:
            if isinstance(result, dict):
                # Extract companies information if available
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
                    # Fallback: convert entire dict to string
                    combined_results.append(str(result))
            else:
                combined_results.append(str(result))
        
        return "\n\n---\n\n".join(combined_results)
    
    def _generate_competitor_analysis(self, company_overview: str, search_data: str) -> str:
        """Generate structured competitor analysis using LLM (enhanced from working code)"""
        prompt = (
            "You are an expert competitive intelligence analyst with deep experience in market research.\n\n"
            "MISSION: Analyze the provided search data and identify ONLY the most direct, relevant competitors.\n"
            "Focus on companies that directly compete for the same customers with similar value propositions.\n\n"
            "STRICT OUTPUT FORMAT:\n\n"
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
            "CRITICAL REQUIREMENTS:\n"
            "- Include ONLY 4-6 most relevant direct competitors\n"
            "- Each bullet point: maximum 15 words\n"
            "- Skip indirect competitors or loosely related companies\n"
            "- Use 'Not available' only if truly no data exists\n"
            "- Prioritize companies that target similar customers with competing solutions\n"
            "- Focus on actionable competitive intelligence\n\n"
            f"COMPANY BEING ANALYZED:\n{company_overview[:500]}\n\n"
            f"SEARCH RESULTS TO ANALYZE:\n{search_data}"
        )
        
        result = llm_service.invoke(prompt)
        
        # Ensure result is string (matching working code pattern)
        if isinstance(result, list):
            result = "\n".join(str(item) for item in result)
        else:
            result = str(result) if result else ""
        
        # Enhanced validation
        if not result or len(result) < 100:
            return (
                "❌ Unable to extract meaningful competitor data from search results.\n\n"
                "**Suggestion:** Try with a more specific company name or URL."
            )
        
        # Clean up formatting
        if "# 🏢 Direct Competitors Analysis" not in result:
            result = "# 🏢 Direct Competitors Analysis\n\n" + result
        
        return result

# Singleton instance
searchscraper_service = SearchScraperService()