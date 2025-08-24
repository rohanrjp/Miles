from pydantic_graph import Graph 
from graph import TeamLeader, StravaCoach, WeatherAssistant, GeneralAssistant, TelegramResponse, RecoveryNode,CalendarAssistant,MemoryNode

assistant_graph = Graph(
        nodes=(MemoryNode, TeamLeader, StravaCoach, WeatherAssistant, GeneralAssistant, RecoveryNode, CalendarAssistant, TelegramResponse)
    )

if __name__=="__main__":
    assistant_graph.mermaid_save("assistant_graph.png",)
    print("Mermaid graph saved to: assistant_graph.png")