import logging
from langchain_core.messages import ToolMessage 
from typing import Any, Annotated 
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,  END 
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
import json
from typing import List 
from pydantic import  Field
from langchain_core.tools import BaseTool


logger = logging.getLogger(__name__)

class ChatAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    hybrid_search: bool

class ChatAgentGraph:
    def __init__(self, llm, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)

        self.graph_builder = StateGraph(ChatAgentState)

        self.graph_builder.add_node("agent", self.chatbot)
        self.graph_builder.add_node("tools", self.tool_node)
        self.graph_builder.add_conditional_edges("agent", tools_condition)
        self.graph_builder.add_conditional_edges(
            "agent",
            self.tool_exists,
            {True: "tools", False: END}
        )
        self.graph_builder.add_edge("tools", "agent")
        self.graph_builder.set_entry_point("agent")
        self.graph_builder.set_finish_point("agent")

        self.graph = self.graph_builder.compile()

    def get_available_tools(self) -> List[BaseTool]:
        return self.tools

    def call_tool(self, tool_call: ToolCall) -> Any:
        tools_by_name = {tool.name: tool for tool in self.get_available_tools()}
        tool = tools_by_name[tool_call["name"]]
        response = tool.invoke(tool_call["args"])
        return response

    def tool_node(self, state: ChatAgentState):
        if not state.get("hybrid_search", True):
            logger.info("[ToolNode] Tool execution skipped due to hybrid_search=False")
            return state

        messages = state['messages']
        last_message = messages[-1]

        tool_messages = []
        logger.debug("************ IN TOOL NODE ************")

        for tool_call in last_message.tool_calls:
            try:
                tool_response = self.call_tool(tool_call)
                
                
                tool_msg = ToolMessage(
                    content="<knowledge>"+json.dumps(tool_response, indent=2)+ "</knowledge>",
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)
                logger.info(f"[ToolNode] Tool executed: {tool_call['name']} → {tool_msg.content}")
            except Exception as e:
                logger.error(f"[ToolNode] Tool call failed: {tool_call['name']} | Error: {e}", exc_info=True)
                continue

        state['messages'] = messages + tool_messages
        return state

    def chatbot(self, state: ChatAgentState):
        messages = state["messages"]
        if state.get("hybrid_search", True):
            new_msg = self.llm_with_tools.invoke(messages)
            logger.debug("[Chatbot] Invoked LLM with tools")
        else:
            new_msg = self.llm.invoke(messages)
            logger.debug("[Chatbot] Invoked LLM without tools")
        return {"messages": messages + [new_msg]}

    def tool_exists(self, state: ChatAgentState):
        if not state.get("hybrid_search", True):
            return False
        last_msg = state['messages'][-1]
        exists = hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0
        logger.debug(f"[Tool Exists] Tool calls present: {exists}")
        return exists

    def invoke(self, state: ChatAgentState, config=None):
        return self.graph.invoke(state, config=config)
   
    def stream_response(self, state: ChatAgentState, config=None):
            for message_chunk, metadata in self.graph.stream(
                state,
                stream_mode="messages",
                config=config,
            ):
                if message_chunk.content:
                    yield message_chunk.content