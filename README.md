# macro-time-machine

What this project is

Macro Time Machine is a long-horizon macro data exploration system for analyzing economic and market indicators across decades of history.

What problem it solves

Macro analysis often suffers from:

inconsistent data frequencies

fragmented datasets

narrative-driven interpretation

lack of historical grounding

This system creates a clean, standardized macro dataset and enables structured slicing of history to analyze regimes, transitions, and long-term behavior.

The system is built in three  layers:

1. Data standardization layer

Raw macro data is:

loaded from CSV formats

normalized to a common schema (Date, Value)

automatically detected as daily/monthly

standardized to monthly frequency

aligned to month-end values

cleaned and saved into a processed data store

This guarantees cross-indicator comparability.

2. Metadata + slicing layer

Each indicator is:

registered with country, category, and display metadata

indexed into a metadata table

queryable by:

fixed time windows (1Y, 3Y, 5Y, 10Y, 20Y, 30Y)

custom date ranges

Every slice produces:

normalized time series

monthly percentage changes

summary statistics

consistent data contracts

3. Interpretation + interface layer

A Streamlit UI provides:

indicator selection by category and country

historical slicing

structured summary metrics

tabular monthly data

AI-assisted interpretation:

AI analysis (Gemini) is:

data-grounded

constrained to the selected slice

prohibited from external storytelling

explicitly backward-looking

Execution flow:

Data preparation

python src/build_processed.py

This:

cleans all raw indicators

standardizes them to monthly

builds metadata registry

Analysis interface:

streamlit run streamlit_app.py

Users can:

select indicators

choose time windows or custom ranges

view historical regimes

inspect changes and volatility

optionally generate AI interpretations

What this system does NOT do

No macro forecasting

No trading signals

No portfolio construction

No prediction models

No optimization logic

This is an analysis engine, not a strategy engin

LLMs are used only for interpretation, not for:

data processing

slicing

statistics

transformations

All quantitative outputs are deterministic.

Intended use

Macro research

Long-horizon analysis

Historical regime study

Educational macro exploration

Analytical tooling experiments

Status

Working system, structured pipeline, exploratory by design.












