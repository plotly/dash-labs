import streamlit as st
import plotly.express as px
# Load data

@st.cache
def load_data():
    df = px.data.iris()
    return df

df = load_data()
feature_cols = [col for col in df.columns if "species" not in col]


st.write("# Iris Dataset")

st.sidebar.write("Options")
x = st.sidebar.selectbox("X Variable", feature_cols)
y = st.sidebar.selectbox("Y Variable", [col for col in feature_cols if col != x])

st.plotly_chart(
    px.scatter(df, x=x, y=y, color="species")
)
