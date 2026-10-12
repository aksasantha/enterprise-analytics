from database.snowflake import get_snowflake_session


def main():
    session = get_snowflake_session()

    result = session.sql("""
        SELECT
            CURRENT_DATABASE() AS DATABASE_NAME,
            CURRENT_SCHEMA() AS SCHEMA_NAME,
            CURRENT_ROLE() AS ROLE_NAME
    """).to_pandas()

    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
    