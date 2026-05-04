# src/main.py
import asyncio
import logging
from src.agent import AgentSession
from src.schema import FullBuild

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    print("Initiating recursive interview... Type 'exit' to quit.\n")

    session = AgentSession()
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Terminating session.")
            break
            
        print("Architect is analyzing market data and calculating geometry...")
        response = await session.chat(user_input)
        
        if isinstance(response, FullBuild):
            print("\n=== FINAL COMPATIBLE BUILD DEPLOYED ===")
            print(f"{'Category':<10} | {'Component Name':<35} | {'Price':<10} | {'Vendor':<10}")
            print("-" * 75)
            for part in response.components:
                print(f"{part.category:<10} | {part.name:<35} | ${part.price:<9.2f} | {part.vendor:<10}")
            print("-" * 75)
            print(f"Total Cost: ${response.total_price:.2f}")
            print(f"System Peak TDP: {response.total_tdp}W")
            print(f"Validation Status: {'PASS' if response.is_compatible else 'FAIL'}")
            
            if response.build_notes:
                print("\nOptimization Notes:")
                for note in response.build_notes:
                    print(f"- {note}")
        else:
            print(f"\nArchitect: {response}")

if __name__ == "__main__":
    asyncio.run(main())