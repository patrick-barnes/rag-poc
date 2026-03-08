import os
import requests
import streamlit as st

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')

st.title('RAG PoC')

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
