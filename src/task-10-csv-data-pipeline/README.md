# Task 10 – CSV Data Pipeline & Exploratory Data Analysis

A reusable Pandas preprocessing pipeline for customer data. It validates an input CSV, reports quality issues, removes duplicates, imputes missing numerical values with medians, validates business rules, engineers features, performs EDA, and exports an ML-ready dataset.

## Structure

- `data/customer_data.csv` – sample input data
- `src/customer_data_pipeline.py` – `CustomerDataPipeline` implementation
- `output/cleaned_customer_data.csv` – generated output

## Run

From this directory, run the pipeline script with Python. It executes the eight required scenarios and then runs the complete sample workflow.

The pipeline requires `pandas` and `numpy`.

## Cleaning and feature engineering

- `Age`, `Income`, and `PurchaseAmount` missing values use median imputation because the median is less sensitive to outliers than the mean.
- Duplicate rows are removed in `cleaned_df`; the raw `df` remains unchanged.
- `IncomePerExperience` is `Income / Experience`, with `0.0` used when experience is zero.
- `PurchaseCategory` is Low for values up to 2,000, Medium above 2,000 through 5,000, and High above 5,000.
- `AgeGroup` is Young for ages below 30, Adult for ages 30–39, and Senior for ages 40 and above.

## Analysis

The pipeline calculates descriptive statistics, a correlation matrix, purchase-status group summaries, high-value customers, sorted purchases, and an EDA summary. Correlation describes linear association, not causation: positive values move together, negative values move oppositely, and values near zero indicate little linear relationship.

`generate_ml_ready_data()` returns `X` with `Age`, `Income`, `Experience`, `PurchaseAmount`, and `IncomePerExperience`, plus `y` containing `Purchased`. `CustomerID` is intentionally excluded.

## Required test cases

The script includes checks for valid CSV input, missing files, wrong extensions, missing required columns, multiple missing values, invalid ages, invalid purchase labels, and zero experience.

## Complexity

For $n$ rows and $m$ columns, most validation, cleaning, feature engineering, and statistics operations are $O(nm)$. Sorting customers is $O(n \log n)$. The main DataFrames and reports require $O(nm)$ space.
