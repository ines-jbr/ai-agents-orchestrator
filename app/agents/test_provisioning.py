from dotenv import load_dotenv
load_dotenv()

from app.agents.provisioning_agent import run_provisioning_agent

if __name__ == "__main__":
    print("Testing AgentProvisioning...\n")
    print("=" * 50)

    result = run_provisioning_agent(
        description="App Node.js avec auto-scaling, 1000 users/jour",
        environment="dev",
        budget_usd=200
    )

    print(result)
    print("=" * 50)
    print("\nTest completed ✅")