#  AI Agents Orchestrator

Orchestration layer that coordinates multiple specialized AI agents for:
- Infrastructure provisioning
- Cost optimization
- DevOps automation
- Deployment

## Tech Stack
Python · LangGraph · CrewAI · FastAPI · RabbitMQ · Docker · PostgreSQL

## Architecture
User → FastAPI → RabbitMQ → Worker (LangGraph) → Agents → PostgreSQL