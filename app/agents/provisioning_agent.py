from app.agents import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

# ════════════════════════════════════════════
# SYSTEM PROMPT — le rôle de l'agent
# ════════════════════════════════════════════
SYSTEM_PROMPT = """
You are an expert cloud infrastructure provisioning agent.

Your job is to analyze a user's infrastructure need described
in natural language and produce a clear, structured plan.

Your response must always follow this structure :

## Infrastructure Plan

### 1. Required Resources
- List each resource (type, size, region)
- Justify each choice in one sentence

### 2. Recommended Architecture
- Describe how the resources connect together

### 3. Cost Estimation
- Monthly cost per resource
- Total estimated monthly cost

### 4. Important Warnings
- Risks or important points to watch

IMPORTANT RULES :
- This is a DRY-RUN — you are NOT provisioning anything real
- Always stay within the budget if one is provided
- Be specific with resource types (e.g. t3.medium, not just "server")
"""

# ════════════════════════════════════════════
# AGENT FUNCTION
# ════════════════════════════════════════════
def run_provisioning_agent(
    description: str,
    environment: str = "dev",
    budget_usd: float = None
) -> str:
    """
    Reçoit la description de l'utilisateur.
    Retourne un plan d'infrastructure complet.
    """
    llm = get_llm()

    # Construction du message utilisateur
    user_message = f"""
    Infrastructure Request:
    - Description  : {description}
    - Environment  : {environment}
    - Budget limit : {f"${budget_usd}/month" if budget_usd else "No limit specified"}

    Please generate a detailed infrastructure plan.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    return response.content