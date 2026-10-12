import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date, timedelta

from services.forex_analytics import get_forex_transactions


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def format_compact(value, prefix=""):
    """Format large numbers using K, M, or B."""

    if pd.isna(value):
        return "—"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{prefix}{value / 1_000:.2f}K"

    return f"{prefix}{value:,.2f}"


def prepare_transactions(df):
    """Prepare transaction columns for analysis."""

    df = df.copy()

    df["TRANSACTION_DATE"] = pd.to_datetime(
        df["TRANSACTION_DATE"],
        errors="coerce",
    )

    df["VOLUME_USD"] = pd.to_numeric(
        df["VOLUME_USD"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["TRANSACTION_DATE", "TRANSACTION_ID"]
    )

    df["VOLUME_USD"] = df["VOLUME_USD"].fillna(0)

    for column in ["BRANCH", "CURRENCY", "CHANNEL"]:
        df[column] = df[column].fillna("Unknown").astype(str)

    return df


# --------------------------------------------------
# Main report
# --------------------------------------------------

def show():

    st.title("Forex Performance")

    st.caption(
        "Monitor business volume, monthly trends, "
        "and operational performance."
    )

    # Load data
    df = prepare_transactions(get_forex_transactions())

    if df.empty:
        st.warning("No Forex transaction data is available.")
        return

    # --------------------------------------------------
    # Filters
    # --------------------------------------------------

    title_col, reset_col = st.columns([5, 1])

    with title_col:
        st.subheader("Filters")

    with reset_col:
        if st.button(
            "Reset filters",
            key="reset_performance_filters",
            use_container_width=True,
        ):
            for key in [
                "performance_date_range",
                "performance_branches",
                "performance_currencies",
                "performance_channels",
            ]:
                st.session_state.pop(key, None)

            st.rerun()

    minimum_date = df["TRANSACTION_DATE"].min().date()
    maximum_date = df["TRANSACTION_DATE"].max().date()

    today = date.today()

    default_end = min(maximum_date, today)

    # Handle datasets containing only future-dated records.
    if default_end < minimum_date:
        default_end = maximum_date

    default_start = max(
        minimum_date,
        default_end - timedelta(days=364),
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_dates = st.date_input(
            "Date range",
            value=(default_start, default_end),
            min_value=minimum_date,
            max_value=maximum_date,
            key="performance_date_range",
        )

    with col2:
        selected_branches = st.multiselect(
            "Branch",
            options=sorted(df["BRANCH"].unique()),
            key="performance_branches",
            help="Leave empty to include all branches.",
        )

    with col3:
        selected_currencies = st.multiselect(
            "Currency",
            options=sorted(df["CURRENCY"].unique()),
            key="performance_currencies",
            help="Leave empty to include all currencies.",
        )

    with col4:
        selected_channels = st.multiselect(
            "Channel",
            options=sorted(df["CHANNEL"].unique()),
            key="performance_channels",
            help="Leave empty to include all channels.",
        )

    # --------------------------------------------------
    # Apply filters
    # --------------------------------------------------

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date, end_date = default_start, default_end

    filtered = df[
        (df["TRANSACTION_DATE"].dt.date >= start_date)
        & (df["TRANSACTION_DATE"].dt.date <= end_date)
    ].copy()

    if selected_branches:
        filtered = filtered[
            filtered["BRANCH"].isin(selected_branches)
        ]

    if selected_currencies:
        filtered = filtered[
            filtered["CURRENCY"].isin(selected_currencies)
        ]

    if selected_channels:
        filtered = filtered[
            filtered["CHANNEL"].isin(selected_channels)
        ]

    st.divider()

    if filtered.empty:
        st.info(
            "No transactions match the selected filters. "
            "Try changing your selections."
        )
        return

    # --------------------------------------------------
    # KPI cards
    # --------------------------------------------------

    total_transactions = filtered["TRANSACTION_ID"].nunique()

    total_usd_volume = filtered["VOLUME_USD"].sum()

    average_transaction_value = (
        total_usd_volume / total_transactions
        if total_transactions
        else 0
    )

    active_branches = filtered["BRANCH"].nunique()

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{total_transactions:,}",
    )

    col2.metric(
        "Total USD Volume",
        format_compact(total_usd_volume, "$"),
    )

    col3.metric(
        "Average Transaction Value",
        format_compact(average_transaction_value, "$"),
    )

    col4.metric(
        "Active Branches",
        f"{active_branches:,}",
    )

    st.divider()

    # --------------------------------------------------
    # Visual 1: Monthly USD volume
    # Native Streamlit line chart
    # --------------------------------------------------

    st.subheader("Monthly Business Trend")

    monthly = filtered.copy()

    monthly["MONTH"] = (
        monthly["TRANSACTION_DATE"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        monthly.groupby("MONTH", as_index=False)
        .agg(
            USD_VOLUME=("VOLUME_USD", "sum"),
            TRANSACTIONS=("TRANSACTION_ID", "nunique"),
        )
        .sort_values("MONTH")
    )

    st.line_chart(
        monthly,
        x="MONTH",
        y="USD_VOLUME",
        x_label="Month",
        y_label="USD volume",
        use_container_width=True,
    )

    st.caption(
        "Shows how USD-equivalent business volume changes "
        "from month to month."
    )

    # --------------------------------------------------
    # Visual 2: Branch contribution
    # Native Streamlit horizontal bar chart
    # --------------------------------------------------

    st.subheader("Branch Contribution")

    branch_data = (
        filtered.groupby("BRANCH", as_index=False)
        .agg(
            USD_VOLUME=("VOLUME_USD", "sum"),
            TRANSACTIONS=("TRANSACTION_ID", "nunique"),
        )
        .sort_values("USD_VOLUME", ascending=False)
    )

    st.bar_chart(
        branch_data,
        x="BRANCH",
        y="USD_VOLUME",
        horizontal=True,
        x_label="Branch",
        y_label="USD volume",
        use_container_width=True,
    )

    st.caption(
        "Compare the total USD volume contributed by each branch."
    )

    # --------------------------------------------------
    # Visual 3: Currency analysis
    # Native Streamlit scatter chart
    # --------------------------------------------------

    st.subheader("Currency Analysis")

    currency_data = (
        filtered.groupby("CURRENCY", as_index=False)
        .agg(
            USD_VOLUME=("VOLUME_USD", "sum"),
            TRANSACTIONS=("TRANSACTION_ID", "nunique"),
        )
    )

    currency_data["AVERAGE_TRANSACTION_VALUE"] = (
        currency_data["USD_VOLUME"]
        / currency_data["TRANSACTIONS"].replace(0, pd.NA)
    )

    st.scatter_chart(
        currency_data,
        x="TRANSACTIONS",
        y="AVERAGE_TRANSACTION_VALUE",
        color="CURRENCY",
        size="USD_VOLUME",
        x_label="Number of transactions",
        y_label="Average transaction value (USD)",
        use_container_width=True,
    )

    st.caption(
        "Compare currencies by transaction count and average "
        "transaction value. Bubble size represents total USD volume."
    )

    # --------------------------------------------------
    # Visual 4: Channel distribution
    # Plotly donut chart: no equivalent native donut component
    # --------------------------------------------------

    st.subheader("Transaction Channel Distribution")

    channel_data = (
        filtered.groupby("CHANNEL", as_index=False)
        .agg(
            TRANSACTIONS=("TRANSACTION_ID", "nunique"),
            USD_VOLUME=("VOLUME_USD", "sum"),
        )
    )

    fig_channel = px.pie(
        channel_data,
        names="CHANNEL",
        values="TRANSACTIONS",
        hole=0.55,
        title="Share of Transactions by Channel",
        hover_data=["USD_VOLUME"],
    )

    fig_channel.update_traces(
        textinfo="percent+label",
    )

    st.plotly_chart(
        fig_channel,
        use_container_width=True,
    )

    st.caption(
        "Shows the percentage of transactions processed through "
        "each channel. Hover for transaction counts and USD volume."
    )


show()