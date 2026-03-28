import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from langchain_core.messages import HumanMessage
from app.services.agent.graph import finance_agent_graph
from app.core.config import settings

def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set.")
        return

    company = settings.TARGET_TICKER
    user_input = f"Evaluate the financial health of {company} and generate a brief advisory memo."
    
    print(f"Starting agent workflow for: {company}...\n")
    print("-" * 50)
    
    inputs = {"messages": [HumanMessage(content=user_input)]}
    
    for event in finance_agent_graph.stream(inputs, stream_mode="values"):
        message = event["messages"][-1]
        
        if message.type == "ai":
            if message.tool_calls:
                print("Invoking tools:")
                for tool in message.tool_calls:
                    print(f" - {tool['name']} with args: {tool['args']}")
            else:
                print("Final Report:\n")
                print(message.content)
                
        elif message.type == "tool":
            print(f"Received feedback from tool: {message.name}")
            
        print("-" * 50)

if __name__ == "__main__":
    main()