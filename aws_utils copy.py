import streamlit as st
import boto3

session = boto3.session.Session(
    aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'],
)

bedrockClient = session.client('bedrock-agent-runtime', 'us-west-2')


@st.cache_data(show_spinner="Searching...")
def getAnswers(query):
    knowledgeBaseResponse = bedrockClient.retrieve_and_generate(
        input={'text': query},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': st.secrets['knowledgeBaseId'],
                'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
                'generationConfiguration': {
                    'inferenceConfig': {
                        'textInferenceConfig': {
                            'maxTokens': 2048,
                            'temperature': 0.8,
                        }
                    }
                }
            },
            'type': 'KNOWLEDGE_BASE'
        })
    st.session_state['response'] = knowledgeBaseResponse


@st.cache_data(show_spinner="Getting Tags...")
def getTags(query):
    pass
