from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, START, END
import operator

from app.agents.provisioning_agent import run_provisioning_agent
from app.agents.cost_agent         import run_cost_agent
from app.agents.devops_agent       import run_devops_agent
from app.agents.deployment_agent   import run_deployment_agent


# ════════════════════════════════════════════════════
# STATE — tous les champs en Annotated pour le parallélisme
# ════════════════════════════════════════════════════
def keep_last(old, new):
    """Garde toujours la dernière valeur écrite"""
    return new

class OrchestratorState(TypedDict):
    user_request : Annotated[Optional[dict], keep_last]
    provisioning : Annotated[Optional[str],  keep_last]
    cost         : Annotated[Optional[str],  keep_last]
    devops       : Annotated[Optional[str],  keep_last]
    deployment   : Annotated[Optional[str],  keep_last]
    final_result : Annotated[Optional[dict], keep_last]
    error        : Annotated[Optional[str],  keep_last]
    status       : Annotated[list,           operator.add]


# ════════════════════════════════════════════════════
# NODES
# ════════════════════════════════════════════════════
def router_node(state: OrchestratorState) -> dict:
    print("  [Router] Analyse de la requête...")
    return {"status": ["routing"]}


def provisioning_node(state: OrchestratorState) -> dict:
    print("  [Provisioning] Génération du plan infra...")
    req = state["user_request"]
    result = run_provisioning_agent(
        description = req["description"],
        environment = req.get("environment", "dev"),
        budget_usd  = req.get("budget_usd")
    )
    return {
        "provisioning" : result,
        "status"       : ["provisioning_done"]
    }


def cost_node(state: OrchestratorState) -> dict:
    print("  [Cost] Optimisation des coûts...")
    req = state["user_request"]
    result = run_cost_agent(
        provisioning_plan = state["provisioning"],
        budget_usd        = req.get("budget_usd")
    )
    return {
        "cost"   : result,
        "status" : ["cost_done"]
    }


def devops_node(state: OrchestratorState) -> dict:
    print("  [DevOps] Génération du pipeline CI/CD...")
    result = run_devops_agent(
        provisioning_plan = state["provisioning"]
    )
    return {
        "devops" : result,
        "status" : ["devops_done"]
    }


def deployment_node(state: OrchestratorState) -> dict:
    print("  [Deployment] Génération des manifests...")
    result = run_deployment_agent(
        provisioning_plan = state["provisioning"]
    )
    return {
        "deployment" : result,
        "status"     : ["deployment_done"]
    }


def aggregator_node(state: OrchestratorState) -> dict:
    print("  [Aggregator] Fusion des résultats...")
    final_result = {
        "provisioning"      : state.get("provisioning"),
        "cost_optimization" : state.get("cost"),
        "devops"            : state.get("devops"),
        "deployment"        : state.get("deployment"),
    }
    return {
        "final_result" : final_result,
        "status"       : ["done"]
    }


# ════════════════════════════════════════════════════
# BUILD GRAPH
# ════════════════════════════════════════════════════
def build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("router",       router_node)
    graph.add_node("provisioning", provisioning_node)
    graph.add_node("cost",         cost_node)
    graph.add_node("devops",       devops_node)
    graph.add_node("deployment",   deployment_node)
    graph.add_node("aggregator",   aggregator_node)

    graph.add_edge(START,          "router")
    graph.add_edge("router",       "provisioning")
    graph.add_edge("provisioning", "cost")
    graph.add_edge("cost",         "devops")
    graph.add_edge("cost",         "deployment")
    graph.add_edge("devops",       "aggregator")
    graph.add_edge("deployment",   "aggregator")
    graph.add_edge("aggregator",   END)

    return graph.compile()


# ════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════
def run_orchestrator(user_request: dict) -> dict:
    graph = build_graph()

    initial_state = {
        "user_request" : user_request,
        "provisioning" : None,
        "cost"         : None,
        "devops"       : None,
        "deployment"   : None,
        "final_result" : None,
        "error"        : None,
        "status"       : []
    }

    print("\n🚀 Démarrage de l'orchestrateur LangGraph...")
    print("=" * 50)

    result = graph.invoke(initial_state)

    print("=" * 50)
    print("✅ Orchestration terminée !\n")

    return result["final_result"]