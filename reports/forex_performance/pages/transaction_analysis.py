from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

    df = df.dropna(subset=["TRANSACTION_DATE", "TRANSACTION_ID"])

    df["VOLUME_USD"] = df["VOLUME_USD"].fillna(0)

    category_columns = [
        "BRANCH",
        "CURRENCY",
        "PRODUCT",
        "TRANSACTION_TYPE",
        "CHANNEL",
    ]

    for column in category_columns:
        df[column] = df[column].fillna("Unknown").astype(str)

    return df


# --------------------------------------------------
# Main report
# --------------------------------------------------


def show():

    st.page_link(
        "reports/forex_performance/pages/home.py",
        label="Home",
        icon=":material/home:",
    )


    st.title("Transaction Analysis")

    st.caption(
        "Explore transaction characteristics, daily activity, "
        "and product-level business patterns."
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
            key="reset_transaction_filters",
            use_container_width=True,
        ):
            for key in [
                "transaction_date_range",
                "transaction_branches",
                "transaction_currencies",
                "transaction_products",
                "transaction_types",
                "transaction_channels",
            ]:
                st.session_state.pop(key, None)

            st.rerun()

    minimum_date = df["TRANSACTION_DATE"].min().date()
    maximum_date = df["TRANSACTION_DATE"].max().date()

    today = date.today()

    default_end = min(maximum_date, today)

    if default_end < minimum_date:
        default_end = maximum_date

    default_start = max(
        minimum_date,
        default_end - timedelta(days=364),
    )

    # First row of slicers
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_dates = st.date_input(
            "Date range",
            value=(default_start, default_end),
            min_value=minimum_date,
            max_value=maximum_date,
            key="transaction_date_range",
        )

    with col2:
        selected_branches = st.multiselect(
            "Branch",
            options=sorted(df["BRANCH"].unique()),
            key="transaction_branches",
            help="Leave empty to include all branches.",
        )

    with col3:
        selected_currencies = st.multiselect(
            "Currency",
            options=sorted(df["CURRENCY"].unique()),
            key="transaction_currencies",
            help="Leave empty to include all currencies.",
        )

    # Second row of slicers
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_products = st.multiselect(
            "Product",
            options=sorted(df["PRODUCT"].unique()),
            key="transaction_products",
            help="Leave empty to include all products.",
        )

    with col2:
        selected_types = st.multiselect(
            "Transaction Type",
            options=sorted(df["TRANSACTION_TYPE"].unique()),
            key="transaction_types",
            help="Leave empty to include all transaction types.",
        )

    with col3:
        selected_channels = st.multiselect(
            "Channel",
            options=sorted(df["CHANNEL"].unique()),
            key="transaction_channels",
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
        filtered = filtered[filtered["BRANCH"].isin(selected_branches)]

    if selected_currencies:
        filtered = filtered[filtered["CURRENCY"].isin(selected_currencies)]

    if selected_products:
        filtered = filtered[filtered["PRODUCT"].isin(selected_products)]

    if selected_types:
        filtered = filtered[filtered["TRANSACTION_TYPE"].isin(selected_types)]

    if selected_channels:
        filtered = filtered[filtered["CHANNEL"].isin(selected_channels)]

    st.divider()

    if filtered.empty:
        st.info(
            "No transactions match the selected filters. Try changing your selections."
        )
        return

    # --------------------------------------------------
    # KPI cards
    # --------------------------------------------------

    total_transactions = filtered["TRANSACTION_ID"].nunique()

    average_transaction_value = filtered["VOLUME_USD"].mean()

    largest_transaction = filtered["VOLUME_USD"].max()

    active_days = filtered["TRANSACTION_DATE"].dt.date.nunique()

    st.subheader("Transaction Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{total_transactions:,}",
    )

    col2.metric(
        "Average Transaction Value",
        format_compact(average_transaction_value, "$"),
    )

    col3.metric(
        "Largest Transaction",
        format_compact(largest_transaction, "$"),
    )

    col4.metric(
        "Active Days",
        f"{active_days:,}",
    )

    st.divider()

    # --------------------------------------------------
    # Visual 1: Interactive transaction matrix
    # Native Streamlit dataframe
    # --------------------------------------------------

    st.subheader("Transaction Analysis Matrix")

    matrix = (
        filtered.groupby(
            [
                "BRANCH",
                "CURRENCY",
                "PRODUCT",
                "TRANSACTION_TYPE",
                "CHANNEL",
            ],
            as_index=False,
        )
        .agg(
            TRANSACTIONS=("TRANSACTION_ID", "nunique"),
            USD_VOLUME=("VOLUME_USD", "sum"),
            AVG_TRANSACTION_VALUE=("VOLUME_USD", "mean"),
        )
        .sort_values(
            "USD_VOLUME",
            ascending=False,
        )
    )

    styled_matrix = matrix.style.background_gradient(
        subset=["USD_VOLUME"],
        cmap="Blues",
    ).format(
        {
            "TRANSACTIONS": "{:,.0f}",
            "USD_VOLUME": "${:,.2f}",
            "AVG_TRANSACTION_VALUE": "${:,.2f}",
        }
    )

    st.dataframe(
        styled_matrix,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    st.caption(
        "Compare transaction count, USD volume, and average "
        "transaction value across branches, currencies, products, "
        "transaction types, and channels. Click column headings to sort."
    )

    st.download_button(
        "Download filtered matrix as CSV",
        data=matrix.to_csv(index=False).encode("utf-8"),
        file_name="transaction_analysis.csv",
        mime="text/csv",
    )

    st.divider()

    # --------------------------------------------------
    # Visual 2: Daily transaction activity
    # Plotly heatmap: no native Streamlit heatmap component
    # --------------------------------------------------

    st.subheader("Daily Transaction Activity")

    daily_counts = (
        filtered.assign(TRANSACTION_DAY=filtered["TRANSACTION_DATE"].dt.normalize())
        .groupby("TRANSACTION_DAY")["TRANSACTION_ID"]
        .nunique()
    )

    # Include dates with no transactions so that they appear
    # as zero-activity days rather than disappearing.
    calendar_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
        name="TRANSACTION_DAY",
    )

    daily_counts = daily_counts.reindex(
        calendar_dates,
        fill_value=0,
    )

    daily = daily_counts.rename("TRANSACTIONS").reset_index()

    daily["WEEK_START"] = daily["TRANSACTION_DAY"] - pd.to_timedelta(
        daily["TRANSACTION_DAY"].dt.weekday,
        unit="D",
    )

    daily["WEEKDAY"] = daily["TRANSACTION_DAY"].dt.day_name()

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    heatmap_data = daily.pivot(
        index="WEEKDAY",
        columns="WEEK_START",
        values="TRANSACTIONS",
    ).reindex(weekday_order)

    # Use the date of each week's Monday as the x-axis label.
    week_labels = [week.strftime("%d %b %Y") for week in heatmap_data.columns]

    # Label approximately every four weeks to reduce clutter.
    tick_positions = list(range(0, len(week_labels), 4))

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=week_labels,
            y=weekday_order,
            colorscale="Blues",
            colorbar={
                "title": "Transactions",
            },
            hovertemplate=(
                "Week starting: %{x}<br>"
                "Day: %{y}<br>"
                "Transactions: %{z:.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig_heatmap.update_layout(
        title="Transaction Count by Day of the Week",
        xaxis_title="Week starting",
        yaxis_title="Day of the week",
    )

    fig_heatmap.update_xaxes(
        tickmode="array",
        tickvals=[week_labels[position] for position in tick_positions],
        ticktext=[week_labels[position] for position in tick_positions],
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True,
    )

    st.caption(
        "Each cell represents a weekday in a particular week. "
        "Darker cells indicate more transactions. Blank cells "
        "represent dates outside the selected range."
    )

    st.divider()

    # --------------------------------------------------
    # Visual 3: Product hierarchy
    # Plotly sunburst: no native Streamlit sunburst component
    # --------------------------------------------------

    st.subheader("Product Composition")

    hierarchy_data = filtered.groupby(
        [
            "PRODUCT",
            "TRANSACTION_TYPE",
            "CHANNEL",
        ],
        as_index=False,
    ).agg(
        USD_VOLUME=("VOLUME_USD", "sum"),
    )

    fig_sunburst = px.sunburst(
        hierarchy_data,
        path=[
            "PRODUCT",
            "TRANSACTION_TYPE",
            "CHANNEL",
        ],
        values="USD_VOLUME",
        color="USD_VOLUME",
        color_continuous_scale="Blues",
        title="USD Volume by Product, Transaction Type, and Channel",
    )

    st.plotly_chart(
        fig_sunburst,
        use_container_width=True,
    )

    st.caption(
        "Explore the hierarchy from product to transaction type "
        "to channel. Larger segments represent greater USD volume."
    )


show()
