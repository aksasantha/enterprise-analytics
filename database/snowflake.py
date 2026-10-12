import streamlit as st


def get_snowflake_session():
    """Return the application's Snowflake session."""
    return st.connection("snowflake").session()