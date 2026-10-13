# Components

This package is reserved for reusable Streamlit interface elements shared by report pages. The current modules are empty placeholders; they define no functions, classes, or reusable behavior.

| Module | Intended responsibility | Current implementation |
|---|---|---|
| charts.py | Shared chart-building or display helpers | Empty |
| filters.py | Shared filter widgets or filter application helpers | Empty |
| metrics.py | Reusable KPI/metric display helpers | Empty |
| navigation.py | Reusable navigation UI | Empty |

These responsibilities are inferred from module names and are intentions only, not existing functionality. The current dashboards build their filters, metrics, navigation links, and charts directly in reports/forex_performance/report.py and reports/forex_performance/pages/. No current application code imports these modules.

When reusable UI behavior is introduced, document the real public functions and callers here. For now, see the [report overview](../reports/forex_performance/README.md) and [page guide](../reports/forex_performance/pages/README.md) for the UI that is actually implemented.
