# for Streamlit env sqlite3 compatibility
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import streamlit_authenticator as stauth
from libs.sidebar import *
from libs.main_layout import *
import json
import os
from openai import OpenAI

# page config
st.set_page_config(page_title="EcoInnovate Assistant", layout="wide", page_icon="🌍")

secrets_dict = {"usernames": {"admin": {"name": "Admin", "password": "admin_123456"}, "tester_1": {"name": "Tester_1", "password": "tester_0123456"}}}

# user login setting
authenticator = stauth.Authenticate(
    secrets_dict,
    st.secrets['cookie']['cookie_name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

# dict(st.secrets['credentials'])
# st.secrets['cookie']['cookie_name'],
# st.secrets['cookie']['key'],
# st.secrets['cookie']['expiry_days']

# render the login module
name, authentication_status, username = authenticator.login()

# authenticating users

if st.session_state["authentication_status"]:

    create_sidebar()

    with st.container():
        cols = st.columns([1, 1, 3, 3, 2])
        cols[0].write(f"Temp: {st.session_state['temperature']}")
        cols[1].write(f"Top-p: {st.session_state['top_p']}")
        cols[2].write(f"Frequency Penalty: {st.session_state['frequency_penalty']}")
        cols[3].write(f"Presence Penalty: {st.session_state['presence_penalty']}")
        with cols[4]:
            os.write(1, b'enter cols4\n')
            authenticator.logout()
            os.write(1, b'log out successfully\n')

if st.session_state["authentication_status"]:
    # define username as usr
    usr = username
    create_main_layout(usr)

elif st.session_state["authentication_status"] is False:
    st.error('Username/Password is incorrect.')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password.')
