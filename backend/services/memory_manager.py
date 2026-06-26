import uuid
import re
from backend.database import supabase

def retrieve_similar_episodic_memory(question: str, current_investigation_id: str) -> dict:
    """
    Finds the most semantically similar past investigation and returns its findings.
    Uses word overlap (Jaccard similarity) on lowercase tokens.
    """
    try:
        investigations = supabase.db_get_investigations()
    except Exception as e:
        print(f"Failed to get investigations for semantic memory: {e}")
        return {"past_finding": "None found. This is a new investigation."}
        
    if not investigations:
        return {"past_finding": "None found. This is a new investigation."}
        
    def calculate_similarity(q1: str, q2: str) -> float:
        s1 = set(re.findall(r"\w+", q1.lower()))
        s2 = set(re.findall(r"\w+", q2.lower()))
        if not s1 or not s2:
            return 0.0
        return len(s1.intersection(s2)) / len(s1.union(s2))

    best_match_id = None
    best_match_question = None
    best_score = 0.0
    
    for inv in investigations:
        inv_id = inv.get("id")
        if inv_id == current_investigation_id:
            continue
            
        inv_question = inv.get("question", "")
        # Only check completed investigations
        if inv.get("state") != "COMPLETED":
            continue
            
        score = calculate_similarity(question, inv_question)
        if score > best_score:
            best_score = score
            best_match_id = inv_id
            best_match_question = inv_question
            
    if best_match_id and best_score > 0.15:
        print(f"[SEMANTIC MEMORY] Found similar past investigation '{best_match_id}' with similarity {best_score:.2f}")
        past_memory = supabase.db_retrieve_memory("episodic", best_match_id)
        if past_memory:
            findings = past_memory.get("findings", "")
            if isinstance(findings, dict):
                findings = findings.get("findings", "")
            # Return findings snippet
            return {
                "past_finding": f"Relevant historical context (from similar query '{best_match_question}'): {findings}"
            }
            
    return {"past_finding": "None found. This is a new investigation."}


def seed_semantic_memory():
    """Seeds business rules and formulas into Semantic Memory if not already seeded."""
    kpis = {
        "revenue_growth": {
            "concept": "Revenue Growth KPI",
            "content": {
                "formula": "MoM Growth = ((Current Month - Prior Month) / Prior Month) * 100",
                "description": "Used by Revenue Agent to verify sales velocity changes."
            }
        },
        "customer_churn": {
            "concept": "Customer Churn KPI",
            "content": {
                "formula": "Churn Rate = (Churned Customers in Segment / Total Customers in Segment) * 100",
                "description": "Used by Customer Agent to identify segments requiring outreach."
            }
        },
        "anomaly_alert_tolerances": {
            "concept": "Risk Alert Tolerances",
            "content": {
                "revenue_decline_alert_threshold": "-10.0%",
                "regional_decline_alert_threshold": "-20.0%",
                "description": "Used by Risk Agent to flag critical revenue declines."
            }
        }
    }
    for key, val in kpis.items():
        try:
            # Check if concept already exists by attempting to retrieve it
            existing = supabase.db_retrieve_memory("semantic", val["concept"])
            if not existing:
                supabase.db_store_memory("semantic", val["concept"], val["content"])
                print(f"Seeded Semantic Memory KPI: {val['concept']}")
        except Exception as e:
            print(f"Failed to seed KPI '{val['concept']}': {e}")

def assemble_context_pipeline(question: str, session_id: str, investigation_id: str) -> tuple[str, str]:
    """
    Executes the Context Assembly Pipeline:
    Question -> Skill Loader -> Working Memory -> Episodic Memory -> Semantic Memory -> Build Context
    """
    from backend import config
    
    def truncate_str(text: str, max_chars: int) -> str:
        if text and len(text) > max_chars:
            return text[:max_chars] + "\n... [Truncated for token management]"
        return text

    # 1. Print Question Trace
    print(f"[ADK TRACE] Question Received: '{question}'")

    # 2. Load active skill
    from backend.services.skill_manager import find_required_skill, load_skill
    skill_name = find_required_skill(question)
    skill_content = load_skill(skill_name)
    skill_content_truncated = truncate_str(skill_content, config.MAX_SKILL_INSTRUCTION_CHARS)
    print(f"[ADK TRACE] Skill Loaded: '{skill_name}' (Truncated: {len(skill_content_truncated) != len(skill_content)})")
    
    # 3. Retrieve / Initialize Working Memory (session based)
    working_data = supabase.db_retrieve_memory("working", session_id)
    if not working_data:
        working_data = {"current_question": question, "status": "initializing"}
        supabase.db_store_memory("working", session_id, working_data)
    working_str = f"Current Investigation: {working_data.get('current_question')}\nCurrent Agent Status: {working_data.get('status')}"
    working_str_truncated = truncate_str(working_str, config.MAX_WORKING_MEMORY_CHARS)
    print(f"[ADK TRACE] Working Memory Retrieved for session '{session_id}'")
    
    # 4. Retrieve / Initialize Episodic Memory (past findings for this investigation using semantic lookup)
    episodic_data = retrieve_similar_episodic_memory(question, investigation_id)
    episodic_str = str(episodic_data)
    episodic_str_truncated = truncate_str(episodic_str, config.MAX_EPISODIC_MEMORY_CHARS)
    print(f"[ADK TRACE] Episodic Memory Retrieved for investigation '{investigation_id}'")
    
    # 5. Load Semantic Memory (KPI definitions)
    revenue_growth_kpi = supabase.db_retrieve_memory("semantic", "Revenue Growth KPI")
    customer_churn_kpi = supabase.db_retrieve_memory("semantic", "Customer Churn KPI")
    risk_tolerances = supabase.db_retrieve_memory("semantic", "Risk Alert Tolerances")
    
    semantic_str = ""
    if revenue_growth_kpi:
        semantic_str += f"- Revenue Growth: {revenue_growth_kpi.get('formula')} ({revenue_growth_kpi.get('description')})\n"
    if customer_churn_kpi:
        semantic_str += f"- Customer Churn: {customer_churn_kpi.get('formula')} ({customer_churn_kpi.get('description')})\n"
    if risk_tolerances:
        semantic_str += f"- Risk Tolerances: MoM Decline > {risk_tolerances.get('revenue_decline_alert_threshold')}, Regional > {risk_tolerances.get('regional_decline_alert_threshold')}\n"
    semantic_str_truncated = truncate_str(semantic_str, config.MAX_SEMANTIC_MEMORY_CHARS)
    print("[ADK TRACE] Semantic Memory Retrieved")
    
    # 6. Build combined context prompt
    context = f"""=== CONTEXT ASSEMBLY PIPELINE ===
[ACTIVE SKILL]
{skill_content_truncated}

[WORKING MEMORY]
{working_str_truncated}

[EPISODIC MEMORY (PAST FINDINGS)]
{episodic_str_truncated}

[SEMANTIC MEMORY (BUSINESS RULES & KPIS)]
{semantic_str_truncated}
================================="""
    
    return context, skill_name

