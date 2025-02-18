import streamlit as st
import pyperclip
import botocore
from aws_utils import getAnswers
import uuid
import toml
import os
import base64
from pathlib import Path


def clear_chat():
    st.session_state["messages"] = []
    st.session_state['sessions'] = []
    st.session_state.pop('response')


def format_chat_history():
    """Format chat history for sharing"""
    formatted = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            role = "User" 
        elif msg["role"] == "assistant":
            role = "Assistant"
        elif msg["role"] == "sources":
            role = "Sources"
        formatted.append(f"{role}: {msg['content']}")
    return "\n\n".join(formatted)


# Page Config
st.set_page_config(page_title="StrataBot", layout="wide")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'sessions' not in st.session_state:
    st.session_state['sessions'] = []

if 'response' not in st.session_state:
    st.session_state['response'] = {}

# Load themes from themes.toml
def load_themes():
    themes_file = os.path.join('.streamlit', 'themes.toml')
    if os.path.exists(themes_file):
        with open(themes_file, 'r') as f:
            themes = toml.load(f)
            return {k.replace('theme.', ''): v for k, v in themes.items()}
    return {}

# Update theme function
def update_theme(theme_dict):
    for key, value in theme_dict.items():
        st._config.set_option(f"theme.{key}", value)  # type: ignore # noqa: SLF001

def img_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# Sidebar
col1, col2, col3 = st.sidebar.columns([1,4,1])
with col2:
    img_path = Path("assets/spd_logo_new.png")
    img_base64 = img_to_base64(img_path)
    st.markdown(
        f'<a href="https://www.superpandas.ai" target="_blank">'
        f'<img src="data:image/png;base64,{img_base64}" width="200">'
        f'</a>', 
        unsafe_allow_html=True
    )

# Create three columns in sidebar for history, share and clear buttons
hist_col, share_col, clear_col = st.sidebar.columns([1,2,2])

# with hist_col:
#     st.markdown('### Chat History')

with share_col:
    if st.button('📋', key='share', help='Copy chat history', disabled=not st.session_state.messages):
        pyperclip.copy(format_chat_history())
        st.toast('Chat history copied to clipboard!')
with clear_col:
    st.button('🗑️', key='clear', on_click=clear_chat, help='Clear chat history')

# Chat history in sidebar with scrollable container
# with st.sidebar.container(height=400, border=False):
#     for session in reversed(st.session_state['sessions']):
#         st.button(
#             session[:30] + "..." if len(session) > 30 else session,
#             key=str(uuid.uuid4()),
#             use_container_width=True,
#             type="secondary",
#             on_click=lambda s=session: getAnswers(s)
#         )

# Add toggle for showing source quotes
show_quotes = st.sidebar.toggle('Show source quotes', value=True)

# Theme selector
themes = load_themes()
theme_names = list(themes.keys())
selected_theme = st.sidebar.selectbox(
    "Select Theme",
    theme_names,
    index=theme_names.index('blue2') if 'blue2' in theme_names else 0
)

# Apply theme if changed
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = selected_theme

if selected_theme != st.session_state.current_theme:
    update_theme(themes[selected_theme])
    st.session_state.current_theme = selected_theme
    st.rerun()

st.sidebar.markdown('---')
st.sidebar.markdown('App Ver : 0.1.0')
st.sidebar.markdown('Developed by : [SuperPandas](https://www.superpandas.ai)')

# Chat interface
st.subheader("Welcome to StrataBot")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "sources":
        continue
        # with st.chat_message("assistant", avatar="📚"):
        #     sources_lines = []
        #     for line in message["content"].split("\n\n"):
        #         if ":" in line and len(line.split("\n")) > 1: # Check if the line contains a source and a quote
        #             source_part = line.split("\n")[0]  # Get the "Source N: location" part
        #             quote_part = line.split("\n")[1]   # Get the quote part
        #             sources_lines.append(source_part)
        #             if show_quotes:
        #                 sources_lines.append(quote_part)
        #     st.markdown("\n\n".join(sources_lines).replace("$", "\$"))
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"].replace("$", "\$"))

# Chat input
if query:= st.chat_input("Ask your question..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    if query not in st.session_state['sessions']:
        st.session_state['sessions'].append(query)
    
    try:
        getAnswers(query)
        # Display assistant response
        with st.chat_message("assistant"):
            response_text = st.session_state['response']['output']['text']
            st.markdown(response_text.replace("$", "\$"))
            feedback = st.feedback()
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Format and add sources as a separate message
        sources_text = []
        info_sources = st.session_state['response']['citations'][0]['retrievedReferences']
        for id, source in enumerate(info_sources):
            location = source['location']['s3Location']['uri'].lstrip("s3://spd-strata-pilot/md/")
            quote = source['content']['text'] if show_quotes else ""
            sources_text.append(f"Source {id+1}: {location}\n{quote}")
        
        # Add sources to chat history
        if sources_text:
            st.session_state.messages.append({
                "role": "sources", 
                "content": "\n\n".join(sources_text)
            })
        
        st.rerun()  # Rerun to update sidebar immediately
        
    except botocore.exceptions.EndpointConnectionError:
        st.error('Error getting answer')

# Only show sources if there's a response
if 'response' in st.session_state and st.session_state['response']:
    # Info Sources
    with st.expander("Sources used for the answer"):
        info_sources = st.session_state['response']['citations'][0]['retrievedReferences']
        for id, source in enumerate(info_sources):
            quote = source['content']['text'].replace("$", "\$")
            location = source['location']['s3Location']['uri'].lstrip("s3://spd-strata-pilot/md/")
            st.markdown(f"**Source {id+1} : {location}**")
            if show_quotes:
                st.markdown(f'Relevant text in the source :\t"{quote}"')
            st.link_button("Go to Source >", "#", disabled=True)
