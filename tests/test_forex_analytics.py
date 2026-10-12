from services.forex_analytics import (
    get_forex_summary,
    get_monthly_performance,
    get_branch_performance,
    get_monthly_running_volume,
)


def main():
    print("\nFOREX SUMMARY")
    print(get_forex_summary().to_string(index=False))

    print("\nMONTHLY PERFORMANCE")
    print(get_monthly_performance().to_string(index=False))

    print("\nBRANCH PERFORMANCE")
    print(get_branch_performance().to_string(index=False))

    print("\nMONTHLY RUNNING VOLUME")
    print(get_monthly_running_volume().to_string(index=False))


if __name__ == "__main__":
    main()