import streamlit as st
from openai import OpenAI
from libs.query_embed import *
from libs.sidebar import *
from libs.img_generator import *

import os


# connect openai key
# OpenAI.api_key = st.secrets["OPENAI_API_KEY"]
OpenAI.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()


# chat limit
CHAT_LIMIT_PER_USER = 3


# convert chat history into string
def format_chat_history(chat_history):
    history_str = ""
    for message in chat_history:
        role = message["role"]
        content = message["content"]["text"]
        history_str += f"{role}: {content}\n"
    return history_str


# create a download button
def create_download_button(chat_history, chat_name):
    chat_history_str = format_chat_history(chat_history)
    # convert chat history into binary for downloading
    chat_history_bytes = chat_history_str.encode("utf-8")
    st.download_button(label="Download Chat History",
                       data=chat_history_bytes,
                       file_name=f"{chat_name}.txt",
                       mime="text/plain",
                       key=f'download_btn')


def create_main_layout(username):

    os.write(1,b'Entered create_main_layout function\n')

    st.header(f'{st.session_state["current_chat"]}')

    # Initialize or retrieve the current chat session's messages
    current_chat = st.session_state["current_chat"]
    if current_chat != "default":

        os.write(1,b'Entered current_chat\n')

        messages_key = f"messages_{current_chat}"
        # initialize chat history
        if messages_key not in st.session_state:

            os.write(1,b'message_key not in session_state\n')

            st.session_state[messages_key] = []
            st.session_state[messages_key].append({"role": "assistant", "content": {"text": "Hi, how can I help you today?", "img": None}})

        if st.session_state[messages_key]:
            for message in st.session_state[messages_key]:
                with st.chat_message(message["role"]):
                    # check if content contains text
                    if "text" in message["content"]:
                        st.markdown(message["content"]["text"])
                    # check if content contains img
                    if "img" in message["content"] and message["content"]["img"] is not None:
                        st.image(message["content"]["img"], caption="Sustainable Product Design", width=500)
        else:
            st.write(f"No messages in chat '{current_chat}'. Start the conversation!")

        # check user's chat limits
        if username not in st.session_state:
            st.session_state[username] = 0  # initialize chat count

        if st.session_state[username] < CHAT_LIMIT_PER_USER:
            
            os.write(1,b'chat count under limits\n')

            def on_submit():
                os.write(1, b'usr entered chat input\n')
                st.session_state[messages_key].append(
                    {"role": "user", "content": {"text": st.session_state["user_input"], "img": None}})
                with st.chat_message("user"):
                    st.markdown(st.session_state[messages_key][-1]["content"]["text"])
                # refresh the chat count if user send messages
                st.session_state[username] += 1

                # Display the chat response in the main chat section
                # if st.session_state[messages_key][-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    conversation_history = st.session_state[messages_key]

                    os.write(1, b'assistant process chat input\n')

                    # text
                    chat_response = process_userinput(st.session_state["user_input"], conversation_history)
                    # img
                    img_response = img_generator(st.session_state["user_input"], chat_response)

                    assistant_message = {"role": "assistant",
                                         "content": {"text": chat_response, "img": img_response}}

                    os.write(1, b'assistant generated response\n')

                    # display text response first
                    message_placeholder.markdown(assistant_message["content"]["text"])
                    # then display image
                    if assistant_message["content"]["img"]:
                        st.image(assistant_message["content"]["img"], caption="Sustainable Product Design",
                                 width=500)

                # Save assistant response for displaying the message chain
                st.session_state[messages_key].append(assistant_message)

                # Place the download button, after the chat input
                create_download_button(st.session_state[messages_key], current_chat)

            # collect and handle user question for the current chat
            prompt = st.chat_input("Input your idea here ...", key="user_input")

            if 'user_input' in st.session_state:
                os.write(1, f"prompt: {st.session_state['user_input']}\n".encode('utf-8'))

            else:
                os.write(1, b'None\n')

        else:
            st.warning("You've reached the chat limit. Please save your chat history.")
            create_download_button(st.session_state[messages_key], current_chat)

    else:
        st.divider()
        st.caption("Notice:")
        st.caption("1. All buttons within the app require a quick double-click to activate.")
        st.caption("2. Every User has the usage limits for EcoInnovate Assistant. The usage limits is set to :blue[10] sessions.")
        st.caption("2. Your conversations are private and not stored beyond your current session. All chat records will be cleared once you refresh the webpage.")
        st.caption("3. You can save your chat history (:blue[text] only) locally by clicking the  *Download Chat History*  button.")
