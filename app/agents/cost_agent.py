from app.agents import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """
You are an expert cloud cost optimization agent.

You receive an infrastructure plan and your job is to:
1. Analyze each resource and its cost
2. Suggest cheaper alternatives where possible
3. Identify unused or oversized resources
4. Propose a final optimized plan with reduced costs

Your response must follow this structure:

## Cost Optimization Report

### 1. Cost Analysis
- Review each resource from the plan

### 2. Optimization Suggestions
- Suggest alternatives with estimated savings

### 3. Optimized Plan
- Final recommended resources after optimization

### 4. Total Savings
- Original cost vs optimized cost

RULES:
- Always stay within the budget if specified
- Prioritize cost reduction without sacrificing performance
- This is a DRY-RUN — nothing is changed in reality
"""

def run_cost_agent(
    provisioning_plan: str,
    budget_usd: float = None
) -> str:
    llm = get_llm()

    user_message = f"""
    Please optimize the following infrastructure plan:

    {provisioning_plan}

    Budget constraint: {f"${budget_usd}/month" if budget_usd else "No limit"}
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    return response.content