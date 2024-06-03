import streamlit as st
from openai import OpenAI

st.set_page_config(page_icon="💬", layout="wide",
                   page_title="Advanced Recovery Systems")

st.subheader("ARS Customer Service Bot", divider="rainbow", anchor=False)

# Initialize the OpenAI client
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

# Retrieve the OpenAI assistant
assistant = client.beta.assistants.retrieve(assistant_id=st.secrets['OPENAI_ASSISTANT_ID'])

# Initialize a thread for the chat
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the user's message
    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Send the user's message to the assistant
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role='user',
        content=prompt,
    )

    # Create a new run and poll for the assistant's response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        instructions="Only user the customer question. If no information is found, please tell the user that you are unable to find the information and offer to connect them with a representative.",
    )

    # Retrieve the assistant's response
    messages = list(client.beta.threads.messages.list(thread_id=st.session_state.thread_id, run_id=run.id))
    message_content = messages[0].content[0].text

    # Display the assistant's response
    with st.chat_message("assistant", avatar='🤖'):
        st.markdown(message_content.value)

    # Append the full response to session_state.messages
    st.session_state.messages.append(
            {"role": "assistant", "content": message_content.value})