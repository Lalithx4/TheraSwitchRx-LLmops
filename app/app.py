import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.pipeline import MedRecommendationPipeline
from dotenv import load_dotenv

st.set_page_config(page_title="Medical Alternatives Recommender",layout="wide")

load_dotenv()

@st.cache_resource
def init_pipeline():
    return MedRecommendationPipeline()

pipeline = init_pipeline()

st.title("Medical Alternatives Recommender System")

query = st.text_input("Enter your medical needs eg. : natural pain relief alternatives for headaches")
if query:
    with st.spinner("Fetching recommendations for you....."):
        response = pipeline.recommend(query)
        st.markdown("### Recommendations")
        st.write(response)

