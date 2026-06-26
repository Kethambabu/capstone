import json
import re
from backend import config
from google import genai
from google.genai import types

def detect_intent_local(question: str) -> dict:
    """Fallback local intent detector using keywords."""
    question_lower = question.lower()
    
    # 1. Determine Category
    if any(k in question_lower for k in ["revenue", "sales", "product", "category", "region"]):
        category = "revenue"
    elif any(k in question_lower for k in ["customer", "churn", "segment", "tier", "standard", "premium"]):
        category = "customer"
    elif any(k in question_lower for k in ["forecast", "projection", "predict", "future", "grow"]):
        category = "forecast"
    elif any(k in question_lower for k in ["risk", "anomaly", "crash", "alert", "decline", "drop"]):
        category = "risk"
    else:
        category = "revenue"
        
    # 2. Determine Question Type & Context Requirement
    # Specific metric questions ask "what is", "how much", "what about my sales in..."
    # Exploratory questions ask "why", "analyze", "explain"
    if any(k in question_lower for k in ["why", "explain", "analyze", "reason", "cause", "diagnostic", "detail", "complete"]):
        q_type = "exploratory"
        need_more_context = True
    elif "drop" in question_lower or "decline" in question_lower or "crash" in question_lower:
        q_type = "exploratory"
        need_more_context = True
    else:
        q_type = "specific_metric"
        need_more_context = False
        
    # 3. Extract Timeframe
    timeframe = None
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
              "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    for m in months:
        if m in question_lower:
            timeframe = m.capitalize()
            break
            
    return {
        "primary_category": category,
        "question_type": q_type,
        "timeframe": timeframe,
        "need_more_context": need_more_context
    }

async def detect_intent(question: str) -> dict:
    """
    Analyzes the user's business question using Gemini to detect:
    - primary_category (revenue, customer, risk, forecast, general)
    - question_type (specific_metric, exploratory)
    - timeframe (e.g. June, May 2026, or null)
    - need_more_context (boolean: whether Risk and Forecast agents are needed)
    """
    if config.MOCK_MODE or not config.GEMINI_API_KEY:
        print("[Intent Detection] Running local keyword detector (Mock/No Key Mode).")
        return detect_intent_local(question)
        
    prompt = f"""You are the Boardroom AI Intent Detector.
Analyze the user's business question: "{question}"

Classify the question into:
1. primary_category: Choose one of:
   - "revenue": for questions about revenue, sales, growth, category performance, regional sales.
   - "customer": for questions about churn, segments, customer retention, tiers.
   - "risk": for questions specifically asking for risks, anomalies, crashes.
   - "forecast": for questions specifically asking for future projections/forecasts.
   - "general": if the query is a comprehensive review or spans multiple distinct domains.
   
2. question_type: Choose one of:
   - "specific_metric": if the user asks a direct question about a specific month/quarter/category (e.g., "What about my sales in June?", "what is the churn rate for premium customers?").
   - "exploratory": if the user asks a "why" question, asks for reasons, deep analysis, or explains drops/declines (e.g., "Why did revenue drop in May?", "Explain regional differences").

3. timeframe: Extracted month, quarter, or year (e.g., "June", "May 2026", or null if none specified).

4. need_more_context: Determine if we need to call supplementary sub-agents (Risk Agent & Forecast Agent) to provide a complete executive answer:
   - If question_type is "specific_metric", this MUST be false by default (unless they ask about a drop/decline).
   - If question_type is "exploratory" or primary_category is "general" or the query involves explaining a decline, this MUST be true.

Provide the response strictly as a JSON object with keys:
"primary_category": string
"question_type": string
"timeframe": string or null
"need_more_context": boolean

Do not include any markdown format or code blocks like ```json. Output raw JSON only."""

    try:
        from backend.services.gemini_client_service import execute_with_retry
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        async def run_detection():
            return client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )
            
        res = await execute_with_retry(run_detection, client=client)
        clean_json = res.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_json)
        
        # Track tokens
        try:
            from backend.services.token_manager import track_agent_tokens
            track_agent_tokens("intent_detector", prompt, res.text)
        except Exception:
            pass
            
        print(f"[Intent Detection] Successfully detected intent: {result}")
        return result
    except Exception as e:
        print(f"[Intent Detection] API failed: {e}. Falling back to local keyword detector.")
        return detect_intent_local(question)
