import streamlit as st

from snowflake.snowpark.functions import (
    avg,
    col,
    count,
    date_trunc,
    sum as sum_,
)

from database.snowflake import get_snowflake_session


TABLE = "UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS"


def get_forex_summary():
    """Return overall Forex performance metrics."""

    transactions = get_snowflake_session().table(TABLE)

    return transactions.agg(
        count("*").alias("TOTAL_TRANSACTIONS"),
        sum_(col("VOLUME_LOCAL")).alias("TOTAL_LOCAL_VOLUME"),
        sum_(col("VOLUME_USD")).alias("TOTAL_USD_VOLUME"),
        avg(col("RATE")).alias("AVERAGE_RATE"),
    ).to_pandas()


def get_monthly_performance():
    """Return monthly transaction counts and USD volume."""

    transactions = get_snowflake_session().table(TABLE)

    return (
        transactions
        .with_column(
            "MONTH",
            date_trunc("MONTH", col("TRANSACTION_DATE")),
        )
        .group_by("MONTH")
        .agg(
            count("*").alias("TOTAL_TRANSACTIONS"),
            sum_(col("VOLUME_USD")).alias("TOTAL_USD_VOLUME"),
        )
        .sort("MONTH")
        .to_pandas()
    )


def get_branch_performance():
    """Return transaction performance by branch."""

    transactions = get_snowflake_session().table(TABLE)

    return (
        transactions
        .group_by("BRANCH")
        .agg(
            count("*").alias("TOTAL_TRANSACTIONS"),
            sum_(col("VOLUME_USD")).alias("TOTAL_USD_VOLUME"),
            avg(col("RATE")).alias("AVERAGE_RATE"),
        )
        .sort(col("TOTAL_USD_VOLUME"), ascending=False)
        .to_pandas()
    )


def get_monthly_running_volume():
    """Return monthly USD volume and its cumulative total."""

    session = get_snowflake_session()

    query = f"""
        WITH MONTHLY_VOLUME AS (
            SELECT
                DATE_TRUNC('MONTH', TRANSACTION_DATE) AS MONTH,
                SUM(VOLUME_USD) AS MONTHLY_USD_VOLUME
            FROM {TABLE}
            GROUP BY 1
        )
        SELECT
            MONTH,
            MONTHLY_USD_VOLUME,
            SUM(MONTHLY_USD_VOLUME) OVER (
                ORDER BY MONTH
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS RUNNING_USD_VOLUME
        FROM MONTHLY_VOLUME
        ORDER BY MONTH
    """

    return session.sql(query).to_pandas()


@st.cache_data(ttl=300)
def get_forex_transactions():
    """
    Retrieve Forex transactions as a Pandas DataFrame.

    Cache the result for five minutes to reduce repeated
    downloads while users interact with the dashboard.
    """

    transactions = get_snowflake_session().table(TABLE)

    return transactions.to_pandas()