"""
Go-To-Market analysis prompts
"""

GTM_PROMPT_TEMPLATE = """You are a professional Go-To-Market (GTM) Strategist.

Based on the provided company (company_url) and competitor data, create a comprehensive GTM strategy.

Your GTM Playbook must include these sections:

1. **Executive Summary** – 2-3 sentences summarizing the GTM approach
2. **Target Market Analysis** – market segments, size, opportunities, positioning
3. **Ideal Customer Profile (ICP)** – demographics, firmographics, pain points, buying behavior
4. **Core Messaging & Value Proposition** – key narratives, positioning statements, differentiators
5. **Pricing Strategy** – pricing model, competitive positioning, justification
6. **Distribution & Sales Strategy** – direct/indirect channels, sales motion, partner ecosystem
7. **Growth Channels & Tactics** – short-term & long-term acquisition channels (SEO, paid ads, partnerships, etc.)
8. **Metrics & KPIs** – 5-8 measurable success indicators to track
9. **Assumptions & Risks** – key assumptions made and potential risks to mitigate

Output Requirements:
- Professional, actionable, presentation-ready format
- Clear structure with headers and bullet points
- Specific, concrete recommendations (not generic advice)
- Base all recommendations on the provided data
- Be realistic about what can be achieved given the company's stage and resources

DATA TO ANALYZE:
{context}

Provide your comprehensive GTM strategy below:
"""