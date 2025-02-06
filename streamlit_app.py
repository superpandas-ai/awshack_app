import streamlit as st
import boto3
import os
import pyperclip

# session = boto3.session.Session(
#     aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
#     aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
#     aws_session_token=os.environ['AWS_SESSION_TOKEN'],
# )

session = boto3.session.Session(
    aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'],
    aws_session_token=st.secrets['AWS_SESSION_TOKEN'],
)

bedrockClient = session.client('bedrock-agent-runtime', 'us-west-2')


@st.cache_data(show_spinner="Searching...")
def getAnswers(questions):
    knowledgeBaseResponse = bedrockClient.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': st.secrets['knowledgeBaseId'],
                'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
                'generationConfiguration': {
                    'inferenceConfig': {
                        'textInferenceConfig': {
                            'maxTokens': 2048,
                            'temperature': 0.5,
                        }
                    }
                }
            },
            'type': 'KNOWLEDGE_BASE'
        })
    return knowledgeBaseResponse


# Page Config
st.set_page_config(page_title="Hallo Hub")  # , layout="wide")

st.title('🎈 Hallo! Hub')

# Search Bar
query = st.text_input("Geben Sie hier Ihre Anfrage ein",
                      "")

if query == "":
    st.stop()

response = getAnswers(query)

# Suggested Answer
st.subheader("Vorgeschlagene Antwort")
with st.container(border=True):
    st.markdown(response['output']['text'])

# Action Buttons
col1, col2, col3, _ = st.columns([1, 1, 1, 2])
with col1:
    if st.button("📋 Kopieren", key='copy_button', disabled=True):
        pyperclip.copy(response['output']['text'])
        st.toast("Copied to clipboard!")
with col2:
    st.button("✏️ Bearbeiten", key='edit_button', disabled=True)
with col3:
    if st.button("🔄 Verfeinern", key='refine_button', disabled=True):
        response = getAnswers(query)

# Related Topics
# st.subheader("Related topics")
# st.write(" ")
# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     st.write("Theme tag")
# with col2:
#     st.write("Theme tag")
# with col3:
#     st.write("Theme tag")
# with col4:
#     st.write("Theme tag")

# Info Sources
st.subheader("Für diese Antwort verwendete Quellen")
info_sources = response['citations'][0]['retrievedReferences']
for id, source in enumerate(info_sources):
    quote = source['content']['text']
    location = source['location']['s3Location']['uri'].lstrip(
        's3://dsee-data/hackathon/')
    with st.expander(f"Quelle {id+1} : {location}"):
        st.write(f'Relevanter Text in der Quelle :\t"{quote}"')
        # st.write(f"Source : {location}")
        st.link_button("Zur Quelle >", "#", disabled=True)
