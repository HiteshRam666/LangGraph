from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage, BaseMessage 
from langgraph.graph import StateGraph, START, END 
from langgraph.checkpoint.memory import InMemorySaver 
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages # Reducer
from typing import TypedDict, List, Dict, Annotated
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import tools_condition, ToolNode
import os 
from dotenv import load_dotenv 
load_dotenv() 

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

class MessageState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

model = ChatOpenAI(model = "gpt-4o-mini")

def make_default_graph():
    """Make a simple LLM Agent"""

    graph = StateGraph(MessageState)
    def call_llm(state: MessageState) -> MessageState:
        return {"messages": [model.invoke(state["messages"])]}


    graph.add_node("agent", call_llm)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END) 

    workflow = graph.compile() 
    return workflow

def make_alternative_graph():
    # Tool Callin agent

    @tool 
    def add(a: int, b: int):
        """
        Adds a and b
        args: 
        a: int 
        b: int 
        """
        return a + b 
    
    tool_node = ToolNode([add])
    model_with_tools = model.bind_tools([add])

    def call_model(state: MessageState):
        return {"messages": model_with_tools.invoke(state["messages"])}

    def should_continue(state: MessageState):
        if state["messages"][-1].tool_calls:
            return "tools" 
        else:
            return END 
        
    workflow = StateGraph(MessageState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)

    agent = workflow.compile() 
    return agent

agent = make_alternative_graph()

# print(agent.invoke({"messages": "Add 10 + 100"})["messages"][-1].content)

agent