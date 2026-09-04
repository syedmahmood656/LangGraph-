import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


# *************************************** utility function *****************************************

def generate_thread_id():
    thread_id = (uuid.uuid4())
    return (thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

# Helper to extract clean text from list/dict format
def extract_text(content):
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)

def load_conversation_history(thread_id):
    # Load conversation history for the given thread_id from session state
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

# st.session_state -> dict -> 
CONFIG = {'configurable': {'thread_id': generate_thread_id()}}  # Generate a unique thread ID for each session to maintain conversation context.


#********************************* session state *****************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []  # Initialize a dictionary to store chat threads, allowing for multiple conversations to be tracked simultaneously.

add_thread(st.session_state['thread_id'])  # Add the current thread ID to the list of chat threads if it's not already present.

#********************************* session state *****************************************
st.title("LangGraph chatbot")

if st.sidebar.button("new chat"):
    reset_chat()

st.sidebar.header('my conversation history')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation_history(thread_id)

        temp = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp.append({'role': role, 'content': extract_text(message.content)})


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream( # st.write function in stramlit helps us to write output in a straming manner just like type weiting effect
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})