# src/agents/mom_agent.py

import json
from google import genai
from configs import settings
from datetime import datetime
from data import property_knowledge

client=genai.Client(api_key=settings.mom_key)

def generate_mom(
    transcript: str,
    action_items: list,
    decisions: list,
    sentiment_timeline: list,
    start_time: float,
    end_time: float,
    business_state: dict
) -> str:

    duration_seconds = end_time - start_time
    duration_minutes = round(duration_seconds / 60.0, 2)
    date_str = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M")

    company_name = property_knowledge.COMPANY_INFO.get("name", "Real Estate Company")
    total_properties = len(property_knowledge.PROPERTIES)

    prompt = f"""
        You are a senior CRM documentation assistant for a large real estate company.

        Generate a PROFESSIONAL Minutes of Meeting (MoM).

        ========================
        CALL METADATA
        ========================
        Company: {company_name}
        Date: {date_str}
        Duration: {duration_minutes} minutes
        Lead Score: {business_state.get("lead_score", 0)}
        Total Properties Available: {total_properties}
        Customer Name: {business_state.get("customer_name")}
        Budget: {business_state.get("budget")}
        Location: {business_state.get("location")}
        Lead Stage: {business_state.get("lead_stage")}
        Business State Summary:
        {json.dumps(business_state, indent=2)}

        ========================
        TRANSCRIPT
        ========================
        {transcript}

        ========================
        ACTION ITEMS
        ========================
        {json.dumps(action_items, indent=2)}

        ========================
        DECISIONS
        ========================
        {json.dumps(decisions, indent=2)}

        ========================
        SENTIMENT TIMELINE
        ========================
        {sentiment_timeline}

        ========================
        INSTRUCTIONS
        ========================
        Create a structured MoM with the following sections:

        1. Call Overview
        2. Customer Requirements
        3. Properties Discussed
        4. Key Decisions
        5. Action Items
        6. Customer Sentiment Summary
        7. Lead Qualification Assessment (Hot / Warm / Cold with reasoning)
        8. Recommended Follow-up Action

        Write in professional corporate tone.
        Do NOT include markdown.
        Return plain structured text.
        """

    try:
        response=client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.4,
            }
        )
        return response.text.strip()
    except Exception as e:
        return f"MoM generation failed: {e}"