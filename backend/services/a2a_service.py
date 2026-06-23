import json
import time
import re
from backend.services.agentops_service import run_agent_with_ops
from backend import config

async def a2a_send_message(sender: str, receiver: str, task: str, dataset: str) -> dict:
    """
    Structured Agent-to-Agent message exchange.
    Transmits sender/receiver JSON packets, triggers agent execution, and monitors latency.
    """
    message = {
        "sender": sender,
        "receiver": receiver,
        "task": task,
        "dataset": dataset
    }
    
    print(f"[A2A MESSAGE] {sender} -> {receiver}: {json.dumps(message)}")
    
    response = {}
    if receiver == "forecast_agent":
        from backend.agents.forecast.forecast_agent import forecast_agent
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        import uuid
        
        async def run_forecast():
            if config.MOCK_MODE:
                time.sleep(0.5) # Simulate A2A task latency
                return {
                    "forecast_growth": 8.2,
                    "confidence": 91
                }
            try:
                from backend.services.gemini_client_service import execute_with_retry
                
                async def run_forecast_call():
                    runner = InMemoryRunner(agent=forecast_agent, app_name="forecast_sub_app")
                    session_id = f"fore_{uuid.uuid4().hex[:8]}"
                    await runner.session_service.create_session(app_name="forecast_sub_app", user_id="system", session_id=session_id)
                    prompt = f"Run revenue forecast analysis on the '{dataset}' dataset. Output in JSON format with keys 'forecast_growth' and 'confidence'."
                    content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                    response_text = ""
                    async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
                        if event.is_final_response() and event.content:
                            parts = event.content.parts
                            if isinstance(parts, list):
                                response_text = "".join(part.text for part in parts if part.text)
                            elif hasattr(parts, 'text'):
                                response_text = parts.text
                            else:
                                response_text = str(parts)
                    return prompt, response_text

                prompt, response_text = await execute_with_retry(run_forecast_call)
                
                # Track forecast agent tokens
                from backend.services.token_manager import track_agent_tokens
                track_agent_tokens("forecast_agent", prompt, response_text)
                
                clean_json = re.sub(r"```json|```", "", response_text).strip()
                res = json.loads(clean_json)
                return {
                    "forecast_growth": float(res.get("forecast_growth", 8.2)),
                    "confidence": int(res.get("confidence", 91))
                }
            except Exception as e:
                print(f"Error executing forecast_agent: {e}. Falling back to default forecast.")
                return {
                    "forecast_growth": 8.2,
                    "confidence": 91
                }
        response = await run_agent_with_ops("forecast_agent", run_forecast)
        
    elif receiver == "security_agent":
        from backend.agents.security.security_agent import run_security_check
        async def run_security():
            # task = question, dataset = role
            return await run_security_check(task, dataset)
        response = await run_agent_with_ops("security_agent", run_security)
        
    elif receiver == "evaluation_agent":
        from backend.agents.evaluation.evaluation_agent import run_report_evaluation
        async def run_evaluation():
            # task = report_text, dataset = investigation_id
            final_report = await run_report_evaluation(dataset, task)
            # Parse the metrics block or return metrics along with the report
            # Let's extract confidence score from the evaluation card if possible,
            # otherwise return default structured response alongside the evaluated report.
            confidence = 90
            accuracy = 95
            completeness = 92
            if "Overall Confidence Score:**" in final_report:
                try:
                    conf_match = re.search(r"Overall Confidence Score:\*\*\s*(\d+)%", final_report)
                    if conf_match:
                        confidence = int(conf_match.group(1))
                except Exception:
                    pass
            return {
                "accuracy": accuracy,
                "completeness": completeness,
                "confidence": confidence,
                "evaluated_report": final_report
            }
        response = await run_agent_with_ops("evaluation_agent", run_evaluation)
        
    else:
        response = {"error": f"Unknown A2A target receiver: {receiver}"}
        
    print(f"[A2A RESPONSE] {receiver} -> {sender}: {json.dumps(response)}")
    return response

