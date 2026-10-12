import streamlit as st

from services.forex_analytics import get_forex_summary



def show():
    st.title("FOREX ANALYTICS")
    st.subheader("Forex Performance & Transaction Analysis")

    st.write(
        "Monitor transaction activity, USD volume, "
        "and Forex business performance across branches."
    )

    st.divider()

    # Fetch summary metrics from Snowflake
    summary = get_forex_summary().iloc[0]

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{int(summary['TOTAL_TRANSACTIONS']):,}",
    )

    col2.metric(
        "Total USD Volume",
        f"${summary['TOTAL_USD_VOLUME'] / 1_000_000:.2f}M",
    )
    col3.metric(
        "Total Local Volume",
        f"{summary['TOTAL_LOCAL_VOLUME'] / 1_000_000:.2f}M",
    )

    col4.metric(
        "Average Exchange Rate",
        f"{summary['AVERAGE_RATE']:.2f}",
    )

    st.divider()

    st.subheader("Explore Your Data")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Forex Performance")
        st.write(
            "Explore monthly trends, compare branch performance, "
            "and analyse currency volumes."
        )

        st.page_link(
            "reports/forex_performance/pages/performance.py",
            label="Open Forex Performance",
            icon=":material/arrow_forward:",
            width="stretch",
        )
    with col2:
        st.markdown("### 📋 Transaction Analysis")
        st.write(
            "Examine transaction distributions, compare channels, "
            "and investigate activity over time."
        )

        st.page_link(
            "reports/forex_performance/pages/transaction_analysis.py",
            label="Open Transaction Analysis",
            icon=":material/arrow_forward:",
            width="stretch",
        )

show()