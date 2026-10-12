# Enterprise Analytics

An external Streamlit application for interactive business analytics
using Snowflake as the data source.

## Project Goals

- Build reusable business reports.
- Keep database access separate from analytics and presentation.
- Provide interactive visualizations and filters.
- Maintain clear documentation and test important functionality.

## Architecture

- `app.py`: Application entry point.
- `config/`: Application configuration.
- `database/`: Database connectivity.
- `services/`: Data retrieval and analytics logic.
- `components/`: Reusable UI components.
- `reports/`: Individual business reports.
- `tests/`: Automated and manual verification.

## Data Sources

Reports connect to Snowflake through the shared database layer.
Each report documents its own database, schema, tables, and metrics.

## Security

Credentials are stored in local Streamlit secrets.
Never commit secrets or other sensitive configuration to Git.

## Reports

- Transaction Analysis: Existing report structure; implementation
  status to be verified.
- Forex Performance: Planned report based on
  `UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS`.

## Change Log

- 2026-10-12: Established project documentation standards.
- 2026-10-12: Documented the current architecture and planned
  Forex Performance report.