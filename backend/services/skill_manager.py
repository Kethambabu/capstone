import os
from pathlib import Path
from backend.database import supabase

SKILL_NAMES = [
    "revenue_analysis",
    "customer_churn",
    "forecasting",
    "risk_detection",
    "executive_reporting"
]

def load_skills_into_db():
    """Reads skills from the local directories and stores them in the database skills table."""
    project_root = Path(__file__).resolve().parent.parent.parent
    skills_dir = project_root / "skills"
    
    for name in SKILL_NAMES:
        skill_file = skills_dir / name / "SKILL.md"
        if skill_file.exists():
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    content = f.read()
                supabase.db_store_skill(name, content)
                print(f"Loaded skill '{name}' from SKILL.md into database.")
            except Exception as e:
                print(f"Failed to read SKILL.md for '{name}': {e}")
        else:
            # Inline fallback instruction if files are not accessible
            fallback_content = f"# {name.replace('_', ' ').title()} Skill\nGoal: Perform analysis of {name}.\nSteps: Load data, run calculations, present results."
            supabase.db_store_skill(name, fallback_content)
            print(f"Stored inline fallback for skill '{name}'.")

def find_required_skill(question: str) -> str:
    """Matches a business question to a skill name based on keyword presence."""
    question_lower = question.lower()
    if "revenue" in question_lower or "sale" in question_lower or "product" in question_lower or "grow" in question_lower:
        return "revenue_analysis"
    elif "churn" in question_lower or "customer" in question_lower or "retention" in question_lower or "segment" in question_lower:
        return "customer_churn"
    elif "forecast" in question_lower or "predict" in question_lower or "future" in question_lower:
        return "forecasting"
    elif "risk" in question_lower or "anomaly" in question_lower or "alert" in question_lower or "drop" in question_lower or "decline" in question_lower:
        return "risk_detection"
    else:
        return "executive_reporting"

def load_skill(name: str) -> str:
    """Retrieves skill instructions from the database, reloading if necessary."""
    skill_content = supabase.db_get_skill(name)
    if not skill_content:
        load_skills_into_db()
        skill_content = supabase.db_get_skill(name)
    return skill_content or f"Skill instruction for '{name}'"

def attach_skill_to_context(question: str, base_context: str = "") -> tuple[str, str]:
    """Finds the appropriate skill for a question, loads it, and prepends it to the context."""
    skill_name = find_required_skill(question)
    instructions = load_skill(skill_name)
    
    print(f"[ADK TRACE] Skill Loaded: '{skill_name}' for question '{question}'")
    
    context = f"""=== ACTIVE AGENT SKILL: {skill_name.upper()} ===
{instructions}
==================================================
{base_context}"""
    return context, skill_name
