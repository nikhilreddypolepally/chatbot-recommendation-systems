import streamlit as st
from openai import OpenAI

# Sidebar for OpenAI API key input
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/nikhilreddypolepally/chatbot/blob/main/chatbot.py)"

# Title and description for the chatbot
st.title("🎓 Chatbot")
st.caption("🚀 Get personalized recommendations and career path guidance")

# Ensure an API key is provided before proceeding
if openai_api_key:
    # Initialize OpenAI API client
    client = OpenAI(api_key=openai_api_key)
    
    # Create an assistant if not already done
    if "assistant" not in st.session_state:

        # Create the assistant
        assistant = client.beta.assistants.create(
            name="Chatbot Assistant",
            description="An AI assistant that answers queries related to course recommendations and career paths.",
            model="gpt-4o"
        )

        # Create a thread for conversation
        thread = client.beta.threads.create()

        # Store the assistant and thread in the session state
        st.session_state["assistant"] = assistant
        st.session_state["thread"] = thread
        st.success("Assistant and thread created successfully!")

    # Initialize the session state for messages
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I am your chatbot assistant. How can I assist you today?"}
        ]

    # Display all messages in the chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input field for user prompt
    if prompt := st.chat_input():
        # Append user message to session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Send the user message to the assistant via the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state["thread"].id,
            role="user",
            content=prompt
        )

        # Run the assistant to generate a response
        run = client.beta.threads.runs.create(
            thread_id=st.session_state["thread"].id,
            assistant_id=st.session_state["assistant"].id
        )

        # Retrieve the assistant's response
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state["thread"].id,
                run_id=run.id
            )
            if run.status == "completed":
                # Retrieve the messages from the thread
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state["thread"].id
                )
                latest_message = messages.data[0]
                response_content = latest_message.content[0].text.value

                # Append assistant's message to session state and display it
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                st.chat_message("assistant").write(response_content)
                break
else:
    st.warning("Please provide your OpenAI API key to continue.")
