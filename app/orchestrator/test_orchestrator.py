from dotenv import load_dotenv
load_dotenv()

from app.orchestrator import run_orchestrator

if __name__ == "__main__":
    result = run_orchestrator({
        "description" : "App Node.js, 1000 users/jour",
        "environment" : "dev",
        "budget_usd"  : 200
    })

    print("\n📋 RÉSULTAT FINAL :")
    print("-" * 40)
    for agent, output in result.items():
        print(f"\n### {agent.upper()} ###")
        print(output[:300])   # affiche les 300 premiers caractères
        print("...")