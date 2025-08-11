from langgraph.graph import StateGraph, START, END 
from langgraph.checkpoint.memory import InMemorySaver 
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages   
load_dotenv() 

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> ChatState:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {'messages': [response]}

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node") 
graph.add_edge("chat_node", END)

checkpointer = InMemorySaver()
workflow = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in workflow.stream(
#     {"messages": HumanMessage(content=), 
#     config={"configurable": {"thread_id": "thread_1"}}, 
#     stream_mode="messages"):

#     if message_chunk.content:
#         print(message_chunk.content, end=" ", flush=True)