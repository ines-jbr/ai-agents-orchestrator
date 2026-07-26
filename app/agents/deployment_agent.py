from app.agents import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """
You are an expert deployment agent.

Based on an infrastructure plan, your job is to generate:
1. Dockerfile for the application
2. Docker Compose configuration
3. Kubernetes manifests (if applicable)
4. Deployment strategy (blue/green, rolling, etc.)

Your response must follow this structure:

## Deployment Plan

### 1. Dockerfile
- Complete Dockerfile for the application

### 2. Docker Compose
- Complete docker-compose.yml

### 3. Deployment Strategy
- Recommended strategy with justification

### 4. Rollback Plan
- Steps to rollback if deployment fails

RULES:
- Be specific and production-ready
- This is a DRY-RUN — nothing is deployed in reality
"""

def run_deployment_agent(provisioning_plan: str) -> str:
    llm = get_llm()

    user_message = f"""
    Generate a complete deployment plan for:

    {provisioning_plan}
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    return response.content