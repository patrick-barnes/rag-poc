import os
import requests
import streamlit as st
import uuid
import datetime

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')

st.title('RAG PoC')

st.header('Upload Document')
uploaded_file = st.file_uploader('Choose a TXT file', type=['txt'])
if uploaded_file is not None:
    if st.button('Ingest Document'):
        with st.spinner('Processing and ingesting...'):
            try:
                text = uploaded_file.read().decode('utf-8')
                doc_id = str(uuid.uuid4())
                payload = [{
                    'id': doc_id,
                    'text': text,
                    'metadata': {
                        'filename': uploaded_file.name,
                        'uploaded_at': str(datetime.datetime.now())
                    }
                }]
                resp = requests.post(f'{BACKEND_URL}/ingest', json=payload)
                if resp.status_code == 200:
                    st.success('Document ingested successfully!')
                else:
                    st.error(f'Ingest failed: {resp.status_code} - {resp.text}')
            except Exception as e:
                st.error(f'Error processing file: {str(e)}')

q = st.text_area('Enter a question')
top_k = st.number_input('Top K', min_value=1, max_value=10, value=4)

if st.button('Ask'):
    if not q.strip():
        st.warning('Please provide a question')
    else:
        with st.spinner('Querying...'):
            resp = requests.post(f'{BACKEND_URL}/query', json={'query': q, 'top_k': top_k})
            if resp.status_code != 200:
                st.error(f'Error: {resp.status_code} - {resp.text}')
            else:
                data = resp.json()
                st.subheader('Answer')
                st.write(data.get('answer'))
                st.subheader('Sources')
                st.write(data.get('sources'))
