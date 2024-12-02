import streamlit as st
import os
from openai import OpenAI

# Streamlit app setup
st.title("Two Agents Talking")

with st.sidebar:
    # Sidebar setup for configurations
    st.header("Configurations")

    with st.expander("Agent A Configurations"):
        agent_a_name = st.text_input("Agent A Name", "Klaus")
        agent_a_personality = st.text_input("Agent A Personality", "Shy and reserved")
        temp_a = st.slider("Temperature for Agent A", 0.0, 1.0, 0.2, 0.1)

    with st.expander("Agent B Configurations"):
        agent_b_name = st.text_input("Agent B Name", "Michael")
        agent_b_personality = st.text_input("Agent B Personality",
                                            "adventures, curious and funny. You like to have a good time, food and nature")
        temp_b = st.slider("Temperature for Agent B", 0.0, 1.0, 0.7, 0.1)

    with st.expander("Conversation Configurations"):
        discussion_topic = st.text_input("Discussion Topic", "Visiting Las Vegas for re:invent and sightseeing")
        convo_length = int(st.slider("Conversation Length", 0.0, 20.0, 10.0, 1.0))
        if st.button("New Conversation"):
            st.session_state.conversation = []

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Display conversation history
for entry in st.session_state.conversation:
    if entry["agent"] == agent_a_name:
        st.chat_message("assistant").write(f"{agent_a_name}: {entry['content']}")
    elif entry["agent"] == agent_b_name:
        st.chat_message("user").write(f"{agent_b_name}: {entry['content']}")

# Instructions for both agents
instructions_a = f"""
You are {agent_a_name}. Respond to {agent_b_name}'s messages and contribute meaningfully to the conversation. 
Conversation Topic: '{discussion_topic}'  
Your personality is {agent_a_personality}. 
"""
instructions_b = f"""
You are {agent_b_name}. Respond to {agent_a_name}'s messages and contribute meaningfully to the conversation. 
Your personality is {agent_b_personality}.
"""

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def prepare_messages(conversation, instructions, agent_name):
    """Prepares the message list for the LLM."""
    messages = [{"role": "system", "content": instructions}]
    for entry in conversation:
        role = "assistant" if entry["agent"] == agent_name else "user"
        messages.append({"role": role, "content": entry["content"]})
    return messages


def get_response(agent_name, instructions, temperature):
    """Generates a response for the given agent."""
    # Prepare interleaved messages with proper roles
    messages = prepare_messages(st.session_state.conversation, instructions, agent_name)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        max_tokens=100,
    )
    return response.choices[0].message.content


# Conversation logic
if st.button("Start Conversation"):
    if not st.session_state.conversation:
        # Start with Agent A's opening message
        opening_message = f"Hello, {agent_b_name}, I want to talk about  {discussion_topic}! "
        st.session_state.conversation.append({"agent": agent_a_name, "content": opening_message})
        st.chat_message("assistant").write(f"{agent_a_name}: {opening_message}")

    # Alternate conversation
    for _ in range(convo_length):  # Limit the conversation to 10 turns for simplicity
        if len(st.session_state.conversation) % 2 == 0:  # Agent A's turn
            response = get_response(agent_a_name, instructions_a, temp_a)
            st.session_state.conversation.append({"agent": agent_a_name, "content": response})
            st.chat_message("assistant").write(f"{agent_a_name}: {response}")
        else:  # Agent B's turn
            response = get_response(agent_b_name, instructions_b, temp_b)
            st.session_state.conversation.append({"agent": agent_b_name, "content": response})
            st.chat_message("assistant").write(f"{agent_b_name}: {response}")

    st.rerun()
