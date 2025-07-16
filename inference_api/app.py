from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from fastapi.responses import StreamingResponse
import asyncio 
app = FastAPI()
class MessageIn(BaseModel):
    role: str
    content: str

from inference_api.agent import ChatAgentGraph
from inference_api.tools import InternetSearchTool
from inference_api.agent_config import Config
from inference_api.models import create_llm

llm = create_llm(Config.MODEL)
search_tool = InternetSearchTool()
tools = [search_tool]
chat_agent = ChatAgentGraph(llm=llm, tools=tools)


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    input_messages = data.get("messages", [])
    hybrid_search = data.get("hybrid_search", True)

    langchain_msgs = []
    for m in input_messages:
        if m["role"] == "user":
            langchain_msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "system":
            langchain_msgs.append(SystemMessage(content=m["content"]))
        elif m["role"] == "assistant":
            langchain_msgs.append(AIMessage(content=m["content"]))
        else:
            langchain_msgs.append(HumanMessage(content=m["content"]))

    state = {
        "messages": langchain_msgs,
        "hybrid_search": hybrid_search,
    }

    updated_state = chat_agent.invoke(state)
    bot_message = updated_state["messages"][-1]

    return {"response": bot_message.content}



import re

knowledge_tag_pattern = re.compile(r'<knowledge>.*?</knowledge>', re.DOTALL)

async def event_stream(state, chat_agent: ChatAgentGraph, config=None):
    gen = chat_agent.stream_response(state, config=config)  # normal generator

    for chunk in gen:  # use normal for, not async for
        # Remove <knowledge>...</knowledge> blocks (if you want)
        filtered_chunk = knowledge_tag_pattern.sub('', chunk)
        if filtered_chunk.strip(): 
            yield f"data: {filtered_chunk}\n\n"
        await asyncio.sleep(0)

        
@app.post("/chat/stream")
async def chat_stream_endpoint(request: Request):
    data = await request.json()
    input_messages = data.get("messages", [])
    hybrid_search = data.get("hybrid_search", True)

    langchain_msgs = []
    for m in input_messages:
        if m["role"] == "user":
            langchain_msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "system":
            langchain_msgs.append(SystemMessage(content=m["content"]))
        elif m["role"] == "assistant":
            langchain_msgs.append(AIMessage(content=m["content"]))
        else:
            langchain_msgs.append(HumanMessage(content=m["content"]))

    state = {
        "messages": langchain_msgs,
        "hybrid_search": hybrid_search,
    }

    # Return streaming response
    return StreamingResponse(
        event_stream(state, chat_agent),
        media_type="text/event-stream",
    )