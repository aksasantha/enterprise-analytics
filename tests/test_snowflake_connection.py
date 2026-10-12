import streamlit as st

st.set_page_config(
    page_title="Snowflake Explorer",
    page_icon="❄️",
    layout="wide",
)

st.title("❄️ Snowflake Connection & Database Explorer")


def find_column(dataframe, expected_name):
    """Find a column after removing surrounding quotes and spaces."""
    for column in dataframe.columns:
        cleaned_column = str(column).strip().strip('"').upper()

        if cleaned_column == expected_name.upper():
            return column

    return None


try:
    # Establish Snowflake connection
    connection = st.connection("snowflake")
    session = connection.session()

    st.success("Connected to Snowflake!")

    # Display connection details
    details = session.sql("""
        SELECT
            CURRENT_ACCOUNT() AS ACCOUNT_NAME,
            CURRENT_USER() AS USERNAME,
            CURRENT_ROLE() AS ROLE_NAME,
            CURRENT_WAREHOUSE() AS WAREHOUSE_NAME
    """).to_pandas()

    st.subheader("Connection Details")
    st.dataframe(details, use_container_width=True)

    # Retrieve databases
    databases = session.sql("SHOW DATABASES").to_pandas()

    st.subheader("Available Databases")

    database_column = find_column(databases, "NAME")

    if database_column is None:
        st.error("Could not identify the database name column.")
        st.dataframe(databases, use_container_width=True)

    elif databases.empty:
        st.warning("No databases are visible to the current role.")

    else:
        database_names = sorted(
            databases[database_column]
            .dropna()
            .astype(str)
            .tolist()
        )

        selected_database = st.selectbox(
            "Select a database",
            database_names,
        )

        st.write(f"**Selected database:** `{selected_database}`")

        # Retrieve schemas
        schemas = session.sql(
            f'SHOW SCHEMAS IN DATABASE "{selected_database}"'
        ).to_pandas()

        st.subheader("Schemas")

        schema_column = find_column(schemas, "NAME")

        if schema_column is None:
            st.error("Could not identify the schema name column.")
            st.dataframe(schemas, use_container_width=True)

        elif schemas.empty:
            st.info("No schemas were found.")

        else:
            schema_names = sorted(
                schemas[schema_column]
                .dropna()
                .astype(str)
                .tolist()
            )

            selected_schema = st.selectbox(
                "Select a schema",
                schema_names,
            )

            st.write(f"**Selected schema:** `{selected_schema}`")

            # Retrieve tables in the selected schema
            tables = session.sql(
                f'SHOW TABLES IN SCHEMA "{selected_database}"."{selected_schema}"'
            ).to_pandas()

            st.subheader("Tables")

            table_name_column = find_column(tables, "NAME")

            if table_name_column is None:
                if tables.empty:
                    st.info("No tables were found in this schema.")
                else:
                    st.error("Could not identify the table name column.")
                    st.dataframe(tables, use_container_width=True)

            else:
                table_names = sorted(
                    tables[table_name_column]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

                if not table_names:
                    st.info("No tables were found in this schema.")

                else:
                    st.dataframe(tables, use_container_width=True)

                    # Inspect table structures
                    st.subheader("Table Structure Explorer")

                    selected_table = st.selectbox(
                        "Select a table to inspect",
                        table_names,
                    )

                    # Retrieve column metadata
                    columns = session.sql(
                        f"""
                        SELECT
                            COLUMN_NAME,
                            DATA_TYPE,
                            IS_NULLABLE,
                            ORDINAL_POSITION
                        FROM "{selected_database}".INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = ?
                          AND TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION
                        """,
                        params=[selected_schema, selected_table],
                    ).to_pandas()

                    st.write(
                        f"**Table:** "
                        f"`{selected_database}.{selected_schema}.{selected_table}`"
                    )

                    st.dataframe(
                        columns,
                        use_container_width=True,
                    )

                    # Preview sample records
                    if st.button("Preview 10 records"):
                        qualified_table = (
                            f'"{selected_database}"'
                            f'."{selected_schema}"'
                            f'."{selected_table}"'
                        )

                        sample = session.table(
                            qualified_table
                        ).limit(10).to_pandas()

                        st.subheader(
                            f"Sample records: {selected_table}"
                        )

                        st.dataframe(
                            sample,
                            use_container_width=True,
                        )

except Exception as error:
    st.error("Unable to retrieve Snowflake information.")
    st.exception(error)