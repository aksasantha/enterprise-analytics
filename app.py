import streamlit as st

from reports.forex_performance import report


st.set_page_config(
    page_title="Forex Analytics",
    page_icon="📊",
    layout="wide",
)

report.show()