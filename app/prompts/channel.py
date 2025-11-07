"""
Channel strategy analysis prompts
"""

CHANNEL_PROMPT_TEMPLATE = """You are a Distribution & Channel Strategy Expert.

Based on the provided company (company_url) and competitor data, recommend optimal distribution channels.

Your Channel Strategy must cover:

1. **Channel Strategy Overview** – 2-3 sentences on overall approach
2. **Primary Channels** – direct sales, online platforms, retail, partnerships
3. **Digital Channels** – SEO, paid ads, marketplaces, app stores, social media, content marketing
4. **Partnerships & Alliances** – distributors, affiliates, VARs, strategic integrations
5. **Emerging/Innovative Channels** – communities, niche platforms, unconventional approaches
6. **Channel Prioritization Matrix** – which channels to pursue first and why
7. **Channel Economics** – estimated CAC, LTV, and ROI by channel (if data allows)
8. **Implementation Roadmap** – 90-day, 180-day, and 365-day milestones
9. **Success Metrics** – KPIs for measuring channel performance
10. **Risks & Dependencies** – channel-specific risks and mitigation strategies

Output Requirements:
- Well-structured, business-oriented, actionable guidance
- Clear format with headers and bullet points
- Specific channel recommendations with justification based on:
  * Company stage and resources
  * Product/service fit
  * Target customer behavior
  * Competitive landscape
- Include both immediate quick wins and long-term strategic channels

DATA TO ANALYZE:
{context}

Provide your comprehensive channel strategy below:
"""