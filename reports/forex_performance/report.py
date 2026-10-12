import streamlit as st


def show():
    pages = [
        st.Page(
            "reports/forex_performance/pages/home.py",
            title="Home",
            url_path="home",
            default=True,
        ),
        st.Page(
            "reports/forex_performance/pages/performance.py",
            title="Forex Performance",
            url_path="performance",
        ),
        st.Page(
            "reports/forex_performance/pages/transaction_analysis.py",
            title="Transaction Analysis",
            url_path="transaction-analysis",
        ),
    ]

    navigation = st.navigation(
        pages,
        position="hidden",
    )

    navigation.run()