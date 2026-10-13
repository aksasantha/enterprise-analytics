import streamlit as st


def show():
    """Configure application navigation and display the selected page."""

    # Register all application pages first
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

    # Initialize navigation before creating links to these pages
    navigation = st.navigation(
        pages,
        position="hidden",
    )

    # Create our custom sidebar
    with st.sidebar:
        st.title("Forex Analytics")
        st.caption("Business Intelligence")

        st.divider()

        st.markdown("### Navigation")

        st.page_link(
            pages[0],
            label="Home",
            icon=":material/home:",
        )

        st.page_link(
            pages[1],
            label="Forex Performance",
            icon=":material/monitoring:",
        )

        st.page_link(
            pages[2],
            label="Transaction Analysis",
            icon=":material/analytics:",
        )

        st.divider()

        st.markdown("### Data Source")
        st.caption("❄️ Snowflake")

    # Run the selected page
    navigation.run()