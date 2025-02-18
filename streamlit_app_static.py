import streamlit as st
import pyperclip
import botocore
from aws_utils import getAnswers, getTags
import uuid


def clear_text():
    st.session_state["text"] = ""
    st.session_state['sessions'] = []


# Page Config
st.set_page_config(page_title="Hallo Hub", layout="wide")

if 'sessions' not in st.session_state:
    st.session_state['sessions'] = []

if 'response' not in st.session_state:
    st.session_state['response'] = {}

# Sidebar
st.sidebar.image('assets/spd_logo_new.png', use_container_width=True)

# st.sidebar.text_input('Feedback')
st.sidebar.markdown('Search History')
container = st.sidebar.container(height=600)
st.sidebar.button('Clear History', disabled=False, on_click=clear_text)
st.sidebar.markdown('App Ver : 0.1.0')

# Search Bar
st.subheader("Please ask your question")
query = st.text_input("input",
                      "", label_visibility="hidden", key='text')

if query == "":
    st.stop()

if query not in st.session_state['sessions']:
    st.session_state['sessions'].append(query)
try:
    getAnswers(query)
except botocore.exceptions.EndpointConnectionError:
    st.error('Error getting answer')

for session in st.session_state['sessions']:
    # st.write()
    container.button(session[:40], on_click=getAnswers(
        session), use_container_width=True, key=str(uuid.uuid4()))

st.subheader("Answer:")  # Suggested Answer
with st.container(border=True):
    st.write(st.session_state['response']['output']['text'].replace("$", "\$"))
    feedback = st.feedback()

# Action Buttons
col1, col2, col3, _ = st.columns([1, 1, 1, 1])
with col1:
    if st.button("📋 Copy", key='copy_button', disabled=True):
        pyperclip.copy(st.session_state['response']['output']['text'])
        st.toast("Copied to clipboard!")
with col2:
    st.button("✏️ Edit", key='edit_button', disabled=True)
with col3:
    if st.button("🔄 Refine", key='refine_button', disabled=False):
        getAnswers(" "+query.strip())

# Info Sources
st.subheader("Sources used for the answer")
info_sources = st.session_state['response']['citations'][0]['retrievedReferences']
for id, source in enumerate(info_sources):
    quote = source['content']['text'].replace("$", "\$")
    location = source['location']['s3Location']['uri'].lstrip(
        's3://dsee-data/hackathon/')
    with st.expander(f"Source {id+1} : {location}"):
        st.markdown(f'Relevant text in the source :\t"{quote}"')
        st.link_button("Go to Source >", "#", disabled=True)
