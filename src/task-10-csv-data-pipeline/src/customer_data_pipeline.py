from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class CustomerDataPipeline:
    """Load, clean, analyze, and export customer data from a CSV file."""

    REQUIRED_COLUMNS = [
        "CustomerID",
        "Age",
        "Income",
        "Experience",
        "PurchaseAmount",
        "Purchased",
    ]
    NUMERIC_COLUMNS = ["Age", "Income", "Experience", "PurchaseAmount", "Purchased"]
    STATISTIC_COLUMNS = ["Age", "Income", "Experience", "PurchaseAmount", "IncomePerExperience"]

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.cleaned_df = None
        self.summary = {}

    def validate_file(self):
        """Validate the path type, existence, and CSV extension."""
        if not isinstance(self.file_path, (str, Path)):
            raise TypeError("File path must be a string or Path.")
        path = Path(self.file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("CSV file does not exist.")
        if path.suffix.lower() != ".csv":
            raise ValueError("Only CSV files are supported.")
        return True

    def load_data(self):
        """Read the validated CSV into the raw DataFrame."""
        self.validate_file()
        self.df = pd.read_csv(self.file_path)
        return self.df

    def validate_columns(self):
        """Ensure all columns required by the pipeline are present."""
        if self.df is None:
            self.load_data()
        missing = [column for column in self.REQUIRED_COLUMNS if column not in self.df.columns]
        if missing:
            raise ValueError(f"Required columns are missing: {', '.join(missing)}")
        return True

    def inspect_dataset(self):
        """Print and return basic shape, schema, and memory information."""
        if self.df is None:
            self.load_data()
        info = {
            "shape": self.df.shape,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
            "data_types": self.df.dtypes.astype(str).to_dict(),
            "memory_usage_bytes": int(self.df.memory_usage(deep=True).sum()),
        }
        print("\n=== Dataset Inspection ===")
        print(f"Shape: {info['shape']}")
        print(f"Rows: {info['rows']}, Columns: {info['columns']}")
        print(f"Columns: {info['column_names']}")
        print("Data types:\n", self.df.dtypes)
        print(f"Memory usage: {info['memory_usage_bytes']} bytes")
        return info

    def generate_quality_report(self):
        """Return quality metrics for every raw column."""
        if self.df is None:
            self.load_data()
        report = pd.DataFrame({
            "data_type": self.df.dtypes.astype(str),
            "missing_count": self.df.isna().sum(),
            "missing_percentage": self.df.isna().mean().mul(100).round(2),
            "unique_values": self.df.nunique(dropna=True),
        })
        self.summary["quality_report"] = report
        print("\n=== Data Quality Report ===")
        print(report)
        return report

    def find_duplicates(self):
        """Return duplicate rows and report their count."""
        if self.df is None:
            self.load_data()
        duplicates = self.df[self.df.duplicated(keep=False)].copy()
        print(f"\nDuplicate rows found: {len(duplicates)}")
        return duplicates

    def remove_duplicates(self):
        """Copy raw data and remove duplicate rows without mutating self.df."""
        if self.df is None:
            self.load_data()
        self.cleaned_df = self.df.drop_duplicates().reset_index(drop=True)
        return self.cleaned_df

    def handle_missing_values(self):
        """Median-impute the specified numerical columns in cleaned data."""
        if self.cleaned_df is None:
            self.remove_duplicates()
        for column in ["Age", "Income", "PurchaseAmount"]:
            self.cleaned_df[column] = self.cleaned_df[column].fillna(self.cleaned_df[column].median())
        return self.cleaned_df

    def _ensure_numeric_columns(self):
        for column in self.NUMERIC_COLUMNS:
            self.cleaned_df[column] = pd.to_numeric(self.cleaned_df[column], errors="coerce")

    def validate_cleaned_data(self):
        """Verify completeness, uniqueness, numeric types, and target values."""
        if self.cleaned_df is None:
            self.handle_missing_values()
        self._ensure_numeric_columns()
        if self.cleaned_df.isna().any().any():
            raise ValueError("Cleaned data contains missing values.")
        if self.cleaned_df.duplicated().any():
            raise ValueError("Cleaned data contains duplicate rows.")
        if not all(pd.api.types.is_numeric_dtype(self.cleaned_df[column]) for column in self.NUMERIC_COLUMNS):
            raise TypeError("Required numerical columns have incorrect data types.")
        if not self.cleaned_df["Purchased"].isin([0, 1]).all():
            raise ValueError("Purchased must contain only 0 or 1.")
        return True

    def detect_invalid_values(self):
        """Raise an error when domain constraints are violated."""
        if self.cleaned_df is None:
            self.handle_missing_values()
        constraints = {
            "Age": self.cleaned_df["Age"] > 0,
            "Income": self.cleaned_df["Income"] >= 0,
            "Experience": self.cleaned_df["Experience"] >= 0,
            "PurchaseAmount": self.cleaned_df["PurchaseAmount"] >= 0,
            "Purchased": self.cleaned_df["Purchased"].isin([0, 1]),
        }
        invalid = [column for column, valid in constraints.items() if not valid.all()]
        if invalid:
            raise ValueError(f"Invalid values detected in: {', '.join(invalid)}.")
        return True

    def create_features(self):
        """Create ratio and purchase-category features."""
        if self.cleaned_df is None:
            self.handle_missing_values()
        experience = self.cleaned_df["Experience"]
        self.cleaned_df["IncomePerExperience"] = np.where(
            experience == 0, 0.0, self.cleaned_df["Income"] / experience
        )
        self.cleaned_df["PurchaseCategory"] = np.select(
            [
                self.cleaned_df["PurchaseAmount"] < 2000,
                self.cleaned_df["PurchaseAmount"] <= 5000,
            ],
            ["Low", "Medium"],
            default="High",
        )
        return self.cleaned_df

    def create_age_group(self):
        """Create Young, Adult, or Senior age groups."""
        if self.cleaned_df is None:
            self.handle_missing_values()
        self.cleaned_df["AgeGroup"] = np.select(
            [
                self.cleaned_df["Age"] < 30,
                self.cleaned_df["Age"] <= 40,
            ],
            ["Young", "Adult"],
            default="Senior",
        )
        return self.cleaned_df

    def get_high_value_customers(self):
        if self.cleaned_df is None:
            self.handle_missing_values()
        return self.cleaned_df[self.cleaned_df["PurchaseAmount"] > 5000].copy()

    def sort_by_purchase_amount(self):
        if self.cleaned_df is None:
            self.handle_missing_values()
        return self.cleaned_df.sort_values("PurchaseAmount", ascending=False).reset_index(drop=True)

    def calculate_statistics(self):
        if self.cleaned_df is None:
            self.create_features()
        stats = {}
        for column in self.STATISTIC_COLUMNS:
            series = self.cleaned_df[column]
            stats[column] = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "minimum": float(series.min()),
                "maximum": float(series.max()),
                "std": float(series.std()),
            }
        self.summary["statistics"] = stats
        return stats

    def calculate_correlation(self):
        if self.cleaned_df is None:
            self.handle_missing_values()
        columns = ["Age", "Income", "Experience", "PurchaseAmount", "Purchased"]
        correlation = self.cleaned_df[columns].corr()
        self.summary["correlation"] = correlation
        return correlation

    def analyze_by_purchase_status(self):
        if self.cleaned_df is None:
            self.handle_missing_values()
        grouped = self.cleaned_df.groupby("Purchased").agg(
            customer_count=("CustomerID", "count"),
            average_age=("Age", "mean"),
            average_income=("Income", "mean"),
            average_purchase_amount=("PurchaseAmount", "mean"),
        )
        self.summary["purchase_status_analysis"] = grouped
        return grouped

    def perform_eda(self):
        if self.cleaned_df is None:
            self.create_age_group()
        eda = {
            "total_customers": int(len(self.cleaned_df)),
            "average_age": float(self.cleaned_df["Age"].mean()),
            "average_income": float(self.cleaned_df["Income"].mean()),
            "median_income": float(self.cleaned_df["Income"].median()),
            "highest_purchase": float(self.cleaned_df["PurchaseAmount"].max()),
            "average_purchase": float(self.cleaned_df["PurchaseAmount"].mean()),
            "purchasers": int((self.cleaned_df["Purchased"] == 1).sum()),
            "non_purchasers": int((self.cleaned_df["Purchased"] == 0).sum()),
            "most_common_age_group": self.cleaned_df["AgeGroup"].mode().iloc[0],
            "most_common_purchase_category": self.cleaned_df["PurchaseCategory"].mode().iloc[0]
            if "PurchaseCategory" in self.cleaned_df else None,
        }
        self.summary["eda"] = eda
        print("\n=== EDA Summary ===")
        for key, value in eda.items():
            print(f"{key}: {value}")
        return eda

    def export_clean_data(self, output_path=None):
        if self.cleaned_df is None:
            self.create_age_group()
        destination = Path(output_path or Path(__file__).parents[1] / "output" / "cleaned_customer_data.csv")
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.cleaned_df.to_csv(destination, index=False)
        print(f"\nCleaned dataset exported to: {destination}")
        return destination

    def generate_ml_ready_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Return selected model features X and Purchased target y."""
        if self.cleaned_df is None:
            self.create_features()
        features = ["Age", "Income", "Experience", "PurchaseAmount", "IncomePerExperience"]
        return self.cleaned_df[features].copy(), self.cleaned_df["Purchased"].copy()

    def run_pipeline(self):
        """Execute the complete validation, cleaning, analysis, and export workflow."""
        self.validate_file()
        self.load_data()
        self.validate_columns()
        self.inspect_dataset()
        self.generate_quality_report()
        self.find_duplicates()
        self.remove_duplicates()
        self.handle_missing_values()
        self.validate_cleaned_data()
        self.detect_invalid_values()
        self.create_features()
        self.create_age_group()
        self.calculate_statistics()
        self.perform_eda()
        self.calculate_correlation()
        self.analyze_by_purchase_status()
        self.export_clean_data()
        return self.summary


def run_required_test_cases(sample_path):
    """Run the eight required scenarios using temporary CSV fixtures."""
    import tempfile

    source = pd.read_csv(sample_path)
    results = []

    def check(name, callback, expected_error=None):
        try:
            callback()
            if expected_error is not None:
                raise AssertionError(f"Expected error containing: {expected_error}")
            results.append((name, "PASS"))
            print(f"{name}: PASS")
        except Exception as error:
            if expected_error is not None and expected_error in str(error):
                results.append((name, "PASS (expected error)"))
                print(f"{name}: PASS (expected error: {error})")
            else:
                results.append((name, f"FAIL: {error}"))
                print(f"{name}: FAIL -> {error}")

    check("Valid CSV", lambda: CustomerDataPipeline(sample_path).run_pipeline())
    check("Missing File", lambda: CustomerDataPipeline(Path(sample_path).parent / "unknown.csv").load_data(), "CSV file does not exist")

    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        wrong_extension = directory / "customers.txt"
        wrong_extension.write_text("not,csv\n1,2\n", encoding="utf-8")
        missing_column = directory / "missing_column.csv"
        source.drop(columns=["Income"]).to_csv(missing_column, index=False)
        missing_values = directory / "missing_values.csv"
        modified = source.copy()
        modified.loc[0, "Age"] = np.nan
        modified.loc[1, "Income"] = np.nan
        modified.loc[2, "PurchaseAmount"] = np.nan
        modified.to_csv(missing_values, index=False)
        invalid_age = directory / "invalid_age.csv"
        modified = source.copy()
        modified.loc[0, "Age"] = -10
        modified.to_csv(invalid_age, index=False)
        invalid_purchased = directory / "invalid_purchased.csv"
        modified = source.copy()
        modified.loc[0, "Purchased"] = 2
        modified.to_csv(invalid_purchased, index=False)
        zero_experience = directory / "zero_experience.csv"
        modified = source.copy()
        modified.loc[0, "Experience"] = 0
        modified.to_csv(zero_experience, index=False)

        def missing_column_case():
            pipeline = CustomerDataPipeline(missing_column)
            pipeline.load_data()
            pipeline.validate_columns()

        check("Wrong Extension", lambda: CustomerDataPipeline(wrong_extension).load_data(), "Only CSV files are supported")
        check("Missing Required Column", missing_column_case, "Required columns are missing")

        def missing_values_case():
            pipeline = CustomerDataPipeline(missing_values)
            pipeline.run_pipeline()
            assert not pipeline.cleaned_df[["Age", "Income", "PurchaseAmount"]].isna().any().any()

        check("Multiple Missing Values", missing_values_case)
        check("Invalid Age", lambda: _run_until_invalid(invalid_age), "Invalid values detected in: Age")
        check("Invalid Purchased", lambda: _run_until_invalid(invalid_purchased), "Invalid values detected in: Purchased")

        def zero_experience_case():
            pipeline = CustomerDataPipeline(zero_experience)
            pipeline.load_data()
            pipeline.remove_duplicates()
            pipeline.handle_missing_values()
            pipeline.detect_invalid_values()
            pipeline.create_features()
            assert pipeline.cleaned_df.loc[0, "IncomePerExperience"] == 0.0

        check("Zero Experience", zero_experience_case)
    return results


def _run_until_invalid(path):
    pipeline = CustomerDataPipeline(path)
    pipeline.load_data()
    pipeline.remove_duplicates()
    pipeline.handle_missing_values()
    pipeline.detect_invalid_values()


def main():
    base_directory = Path(__file__).parents[1]
    sample_path = base_directory / "data" / "customer_data.csv"
    print("=== Required Test Cases ===")
    run_required_test_cases(sample_path)
    print("\n=== Full Pipeline ===")
    CustomerDataPipeline(sample_path).run_pipeline()


if __name__ == "__main__":
    main()
