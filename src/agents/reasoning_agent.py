import json
import re
from google import genai
from configs import settings
from configs.prompts import REASONING_PROMPT
from utils.logger import logger
from data import property_knowledge

client = genai.Client(api_key=settings.reasoning_key)


def reason_about_user(user_text: str, summary: str, entities: dict) -> dict:

    company_info = property_knowledge.COMPANY_INFO
    properties_sample = property_knowledge.PROPERTIES[:4]
    loan_info = property_knowledge.LOAN_INFO
    discount_policy = property_knowledge.DISCOUNT_POLICY

    text_lower = user_text.lower()
    extra_context = ""

    loan_keywords = ["loan", "emi", "bank", "interest", "mortgage", "finance", "funding"]
    discount_keywords = ["discount", "offer", "festival", "deal", "negotiable"]

    if any(word in text_lower for word in loan_keywords):
        extra_context += f"\nLoan Information:\n{json.dumps(loan_info, indent=2)}"

    if any(word in text_lower for word in discount_keywords):
        extra_context += f"\nDiscount Policy:\n{json.dumps(discount_policy, indent=2)}"

    company_context = f"""
Company Name: {company_info.get("name")}
Established: {company_info.get("established")}
Head Office: {company_info.get("head_office")}
Customer Rating: {company_info.get("customer_rating")}

Sample Properties:
{json.dumps(properties_sample, indent=2)}

{extra_context}
"""

    prompt = REASONING_PROMPT.format(
        summary=summary,
        entities=json.dumps(entities),
        user_text=user_text,
        company_context=company_context
    )

    try:
        stream = client.models.generate_content_stream(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.2,
            }
        )
        full_text = ""
        for chunk in stream:
            if chunk.text:
                full_text += chunk.text
        
        text = full_text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))

            if not result.get("final_response"):
                result["final_response"] = "Could you please clarify that?"

            return result

        logger.error("No JSON found in reasoning response.")

    except Exception as e:
        logger.error(f"Reasoning model call failed: {e}")

    return {
        "intent": "unknown",
        "entities": {},
        "sentiment": "neutral",
        "final_response": "I'm sorry, I am facing a temporary issue. Could you please repeat that?",
        "lead_stage": "new",
        "end_call": False
    }