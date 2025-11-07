import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="AI Tsunami", layout="wide")
st.title("AI로 쓰나미 예측하고, 행동으로 이어가기")

@st.cache_resource
def load_model():
    return joblib.load("rf.pkl")  # 리포지토리에 포함했을 때

@st.cache_data
def load_sample():
    return pd.read_csv("sample_quake.csv")

model = load_model()
df = load_sample()
st.dataframe(df.head())
st.success("앱 로딩 성공! 이제 기능을 붙이면 됩니다.")
