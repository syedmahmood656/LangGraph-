from langchain_google_genai import ChatGoogleGenerativeAI

from typing import TypedDict, Annotated
import os

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv


load_dotenv() # helps to access spi keys form .env file


# Initialize Gemini 2.5 Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.7,
    api_key="API",  # Paste your key inside quotes
)

class Chatstate(TypedDict): # typeddict : Ensures type safety across state updates.
    messages : Annotated[list[BaseMessage],add_messages] # annotated : used to make a list of states - usually changed at every state
                                        #add messages : used to kind of save every state throught of worlflow


# here chat node takes the state and use llm to generate answers and the state is updated in retrun 
def chat_nodes(state:Chatstate):
    message = state['messages']
    response = llm.invoke(message)
    return{'messages':[response]}

#checkpointer : A state-persistence mechanism. It stores the state snapshot of the graph in RAM after each step
checkpointer = InMemorySaver()

# defining graph

graph = StateGraph(Chatstate)

graph.add_node("chat_node",chat_nodes)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpointer)