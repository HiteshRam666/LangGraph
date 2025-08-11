from pydantic import BaseModel, Field 
from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware 
from typing import List, Dict, Literal, Optional
from langgraph_backend import workflow 
from langchain_core.messages import HumanMessage 

app = FastAPI(title="LangGraph Chatbot API", version="1.0.0")

# CORs 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "thread_1"

class ChatResponse(BaseModel):
    message: str
    thread_id: str

@app.get("/")
async def root():
    return {"message": "LangGraph Chatbot API is running"}

@app.post("/chat", response_model = ChatResponse)
async def chat(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        
        response = workflow.invoke(
            {"messages": [HumanMessage(content = request.message)]}, 
            config = config
        )

        ai_message = response["messages"][-1].content
        
        return ChatResponse(
            message=ai_message, 
            thread_id=request.thread_id
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}