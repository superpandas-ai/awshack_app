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
st.sidebar.image('assets/dsee.png', use_container_width=True)

# st.sidebar.text_input('Feedback')
st.sidebar.markdown('Sitzungsverlauf')
container = st.sidebar.container(height=600)
st.sidebar.button('Verlauf löschen', disabled=False, on_click=clear_text)
st.sidebar.markdown('App Ver : 0.1.0')

# Search Bar
st.subheader("Geben Sie hier Ihre Anfrage ein")
query = st.text_area("input",
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


st.sidebar.markdown('Help: mailto://help@d-s-e-e.de')
st.sidebar.markdown('App Ver : 0.1.0')

st.subheader("Vorgeschlagene Antwort")  # Suggested Answer
with st.container(border=True):
    st.markdown(st.session_state['response']['output']['text'])
    feedback = st.feedback()

# Action Buttons
col1, col2, col3, _ = st.columns([1, 1, 1, 1])
with col1:
    if st.button("📋 Kopieren", key='copy_button', disabled=True):
        pyperclip.copy(st.session_state['response']['output']['text'])
        st.toast("Copied to clipboard!")
with col2:
    st.button("✏️ Bearbeiten", key='edit_button', disabled=True)
with col3:
    if st.button("🔄 Verfeinern", key='refine_button', disabled=False):
        getAnswers(" "+query.strip())

# Related Topics
# st.subheader("Related topics")
# st.write(" ")
# tags = getTags(query)
# cols = st.columns(4)
# for col, tag_val in zip(cols, *list(tags.items())):
#     with col:
#         st.markdown(tag_val)
#         st.button(tag_val[0],type='tertiary') # add color based on confidence level

# Info Sources
st.subheader("Für diese Antwort verwendete Quellen")
info_sources = st.session_state['response']['citations'][0]['retrievedReferences']
for id, source in enumerate(info_sources):
    quote = source['content']['text']
    location = source['location']['s3Location']['uri'].lstrip(
        's3://dsee-data/hackathon/')
    with st.expander(f"Quelle {id+1} : {location}"):
        st.write(f'Relevanter Text in der Quelle :\t"{quote}"')
        st.link_button("Zur Quelle >", "#", disabled=True)
