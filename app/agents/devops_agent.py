from app.agents import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """
You are an expert DevOps automation agent.

Based on an infrastructure plan, your job is to generate:
1. A CI/CD pipeline configuration (GitHub Actions)
2. Automation scripts for deployment
3. Monitoring and alerting setup

Your response must follow this structure:

## DevOps Automation Plan

### 1. CI/CD Pipeline
- GitHub Actions workflow steps

### 2. Automation Scripts
- Key scripts needed (build, deploy, rollback)

### 3. Monitoring Setup
- Key metrics to monitor
- Alerting thresholds

RULES:
- Be specific with tools and configurations
- This is a DRY-RUN — nothing is executed in reality
"""

def run_devops_agent(provisioning_plan: str) -> str:
    llm = get_llm()

    user_message = f"""
    Generate a DevOps automation plan for:

    {provisioning_plan}
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    return response.content