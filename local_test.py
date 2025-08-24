
import asyncio
from models.domain import User
from graph import run_graph

async def main():
    user = User(name="Rohan Paul", email="rohan1007rjp@gmail.com", interests=["running", "coding"],home_city="Chennai")
    input_request = "should i run today?"
    input_request1 = "whats the weather like?"
    result = await run_graph(input_request1, user)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
