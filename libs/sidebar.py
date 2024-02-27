import streamlit as st
import os


def init_default_params():
    # Initialize model parameters for the new chat
    st.session_state['current_chat'] = 'default'
    st.session_state['temperature'] = 0.6
    st.session_state['top_p'] = 1.0
    st.session_state['presence_penalty'] = 0.0
    st.session_state['frequency_penalty'] = 0.0
    st.rerun()  # Refresh to show the new chat


def add_chat():
    # Function to add a new chat
    st.session_state['current_chat'] = st.session_state['chat_name']
    os.write(1, f'Chat: {st.session_state.current_chat}\n'.encode('utf-8'))
    if st.session_state['current_chat'] not in st.session_state['chats']:
        st.session_state['chats'].append(st.session_state['current_chat'])


def delete_chat():
    # Function to delete a chat
    chat_name = st.session_state['current_chat']
    if chat_name and chat_name in st.session_state['chats']:
        st.session_state['chats'].remove(chat_name)
        # Remove the model parameters associated with this chat
        init_default_params()
        st.rerun()  # Refresh to reflect the deletion
    elif chat_name:
        st.error("This chat does not exist.")


# callback functions for when parameters change
def temp_slider():
    st.session_state['temperature'] = st.session_state.temperature_slider

def top_p_slider():
    st.session_state['top_p'] = st.session_state.top_p_slider

def presence_penalty_slider():
    st.session_state['presence_penalty'] = st.session_state.presence_penalty_slider

def frequency_penalty_slider():
    st.session_state['frequency_penalty'] = st.session_state.frequency_penalty_slider

def callback_fun():
    pass


# Sidebar for model settings and chat history
def create_sidebar():

    # initialize session state
    if 'chats' not in st.session_state:
        st.session_state['chats'] = []
        init_default_params()

    with st.sidebar:
        st.title("🌳 EcoInnovate Assistant")
        st.caption("Please create a new chat to begin a conversation.")

        # model settings
        st.markdown("Model Parameter Settings:")
        st.caption("By adjusting these parameters, you can control how the assistant behaves, such as reliability, creativity, and the style of interactions.")
        temperature = st.slider(
            label="Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state['temperature'],
            step=0.1,
            help="""The temperature setting controls the randomness of the output: higher values increase randomness, while lower values, especially closer to 0, result in more predictable outputs. 
            It is suggested to adjust either this setting or top_p, but not both at the same time.""",
            key='temperature_slider',
            on_change=temp_slider,
        )
        top_p = st.slider(
            label="Top P",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state['top_p'],
            step=0.1,
            help="""Top-p sampling focuses on the model's top predictions that make up the top_p percentage of the total probability. 
            For example, a top-p value of 0.1 refers to the model only considers tokens within the top 10% of the probability mass.""",
            key='top_p' + '_slider',
            on_change=top_p_slider,
        )
        presence_penalty = st.slider(
            label="Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state['presence_penalty'],
            step=0.1,
            help="""Positive values penalize new tokens based on whether they already appear in the generated text,
             which may encourage the model to explore new topics.""",
            key='presence_penalty' + '_slider',
            on_change=presence_penalty_slider,
        )
        frequency_penalty = st.slider(
            label="Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state['frequency_penalty'],
            step=0.1,
            help="""Positive values penalize new tokens based on their existing frequency in the generated text, 
            which may reduce the model's likelihood to repeat the same phrases.""",
            key='frequency_penalty' + '_slider',
            on_change=frequency_penalty_slider,
        )
        st.caption("[More Infor about model's parameters](https://platform.openai.com/docs/api-reference/completions/create)")

        # chat management
        usr_input = st.text_input("Input chat name:", key="chat_name", on_change=None, args=None)
        if st.button("Create"):
            os.write(1, b'button created\n')
            add_chat()

        # display chat history
        st.header("Chat History")
        for chat_name in st.session_state['chats']:
            with st.container():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if st.button(chat_name, key=f"chat_{chat_name}"):
                        st.session_state['current_chat'] = chat_name
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_name}"):
                        delete_chat()

