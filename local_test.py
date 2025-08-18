
import asyncio
from models.domain import User
from graph import run_graph

async def main():
    user = User(name="Test User", email="test@example.com", interests=["running", "coding"])
    input_request = "should i run today?"
    result = await run_graph(input_request, user)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
