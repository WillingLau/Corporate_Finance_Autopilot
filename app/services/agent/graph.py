import json
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.services.agent.tools import AGENT_TOOLS

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

SYSTEM_PROMPT = """
You are an elite Corporate Finance Advisor and Lead Investment Banking Analyst.
Your objective is to assess the financial health of public companies, synthesize quantitative models with qualitative market dynamics, and deliver actionable, institutional-grade strategic advisory.

### Execution Guidelines & Chain of Thought:
1. **Information Gathering:** Always invoke `search_market_news` first to grasp the company's current strategic narrative, macroeconomic headwinds, or tailwinds.
2. **Quantitative Anchoring:** Invoke `generate_financial_forecast` to obtain hard data. You MUST anchor your analysis on the Base, Upside, and Downside scenarios provided by this tool. 
3. **Synthesis & Reasoning:** Do not merely repeat the data. Explain *why* the Upside or Downside scenarios might occur by connecting the financial forecasts with the recent news you retrieved. 
4. **Strict Factuality:** Never hallucinate financial figures. If a tool fails or returns insufficient data, explicitly state this limitation. Avoid presenting guesses as facts and label any uncertainties in your forward-looking statements.

### Required Output Structure (Use Markdown):
Format your response as a professional Financial Advisory Memo:

## I. Executive Summary & Market Context
- Provide a concise overview of the company's current market positioning.
- Cite specific recent news or strategic moves retrieved from your search.

## II. Financial Scenario Analysis
- **Base Case:** Briefly outline the projected trajectory based on historical CAGR.
- **Upside vs. Downside:** Detail the drivers for the optimistic and pessimistic scenarios. (e.g., "The upside scenario (+5%) could be catalyzed by the recent announcement regarding...")

## III. Strategic Capital Advisory
- Based strictly on the synthesized data, provide 2-3 actionable corporate finance recommendations (e.g., M&A opportunities, share buybacks, debt restructuring, or R&D capital allocation).

## IV. Mandatory Disclaimer
Must identically include: "**DISCLAIMER:** This report is AI-generated. It contains forward-looking statements subject to uncertainty. This is NOT investment advice, financial guidance, or a reliable basis for trading decisions. All figures and scenarios are hypothetical."
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
model_with_tools = llm.bind_tools(AGENT_TOOLS)

tools_by_name = {tool.name: tool for tool in AGENT_TOOLS}

def call_model(state: AgentState):
    messages = state["messages"]
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    response = model_with_tools.invoke([system_message] + messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    outputs = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        try:
            tool_result = tools_by_name[tool_name].invoke(tool_args)
            result_str = tool_result if isinstance(tool_result, str) else json.dumps(tool_result, ensure_ascii=False)
        except Exception as e:
            result_str = f"Error executing {tool_name}: {str(e)}"
            
        outputs.append(
            ToolMessage(
                content=result_str,
                name=tool_name,
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    if not last_message.tool_calls:
        return "end"
    return "continue"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

workflow.add_edge("tools", "agent")
finance_agent_graph = workflow.compile()