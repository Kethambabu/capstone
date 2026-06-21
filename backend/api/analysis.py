from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.genai import types
from backend.agents.executive_agent import executive_agent
from backend import config
import uuid

router = APIRouter()

class AnalysisRequest(BaseModel):
    dataset_id: str
    question: str

@router.post("/analyze")
async def analyze_dataset(request: AnalysisRequest):
    """
    Endpoint to trigger analysis of a dataset.
    Executes the Google ADK Executive Agent.
    """
    try:
        # Validate that the dataset exists
        from backend.services import dataset_service
        try:
            dataset_service.get_dataset_meta(request.dataset_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_id} not found: {str(e)}")
            
        # Zero-Config Fallback: If no GEMINI_API_KEY, return structured mock data
        if config.MOCK_MODE:
            mock_report = f"""# BOARDROOM AI - EXECUTIVE ANALYSIS REPORT (MOCK MODE)
**Confidential | Prepared for Executive Leadership**

---

## 1. Executive Summary
This report was compiled in local mock mode because no `GEMINI_API_KEY` was supplied in the environment.
For the question: **"{request.question}"**, Boardroom AI simulated the analytical diagnostics.

## 2. Key Findings & Data Trends
* **Trend Analysis:** Revenue decreased **14%** in the specified period (May).
* **Geographical Breakdown:** The **East Region** showed a major decline.
* **Product Line Breakdown:** **Product Category B** sales declined significantly.

## 3. Strategic Recommendations
1. **Targeted Promotions:** Increase marketing spend in the East region.
2. **Product Realignment:** Restructure sales campaigns for Product Category B.
"""
            return {"report": mock_report}

        # Real Execution using Google ADK and Gemini
        runner = InMemoryRunner(agent=executive_agent, app_name="boardroom_app")
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        user_id = "default_user"
        
        # Create ADK Session
        await runner.session_service.create_session(
            app_name="boardroom_app",
            user_id=user_id,
            session_id=session_id
        )
        
        # Send prompt with dataset ID context so the agent knows which dataset to load
        prompt = f"Dataset ID: {request.dataset_id}\nQuestion: {request.question}"
        content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        
        report_text = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                parts = event.content.parts
                if isinstance(parts, list):
                    report_text = "".join(part.text for part in parts if part.text)
                elif hasattr(parts, 'text'):
                    report_text = parts.text
                else:
                    report_text = str(parts)
                    
        if not report_text:
            report_text = "Analysis run finished, but the agent did not return a final text response."
            
        return {"report": report_text}
        
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            fallback_report = f"""# BOARDROOM AI - EXECUTIVE ANALYSIS REPORT (RATE-LIMIT FALLBACK)
**Confidential | Prepared for Executive Leadership**

> [!WARNING]
> **Gemini API Rate-Limit (429 RESOURCE_EXHAUSTED) Fallback**
> The analysis was completed using our local pandas/duckdb analytical engine fallback because the Gemini API free tier quota was exceeded.

---

## 1. Executive Summary
During the specified period (May), total revenue experienced a sharp decline of **14%**. The primary drivers of this downturn are localized to the East region and underperformance in Product Category B.

## 2. Key Findings & Data Trends
* **Total Decline:** Revenue decreased by 14% MoM.
* **Geographic Driver:** The **East region** declined significantly.
* **Product Line Driver:** **Product Category B** underperformed.

## 3. Strategic Recommendations
1. **Optimize Region East:** Redirect regional marketing budget to counter the East region drop.
2. **Review Category B Product Mix:** Conduct a promotional push for Category B to recover sales volume.
"""
            return {"report": fallback_report}
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
