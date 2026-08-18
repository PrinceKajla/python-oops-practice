import pandas as pd


class PandasDataAnalyzer:
    """Analyze and clean a tabular customer dataset for machine learning preparation."""

    REQUIRED_COLUMNS = ["Customer", "Age", "Income", "Experience", "Purchased"]

    def __init__(self, data):
        self.data = data
        self.df = None
        self.cleaned_df = None

    def create_dataframe(self):
        """Convert the input list of dictionaries into a pandas DataFrame."""
        if not isinstance(self.data, list):
            raise TypeError("Input must be a list of records.")

        if len(self.data) == 0:
            raise ValueError("Dataset cannot be empty.")

        if not all(isinstance(record, dict) for record in self.data):
            raise TypeError("Each record must be a dictionary with column names and values.")

        self.df = pd.DataFrame(self.data)

        if self.df.empty:
            raise ValueError("Dataset cannot be empty.")

        missing_required_columns = [
            column for column in self.REQUIRED_COLUMNS if column not in self.df.columns
        ]
        if missing_required_columns:
            raise ValueError(
                "Dataset is missing required columns: " + ", ".join(missing_required_columns)
            )

        return self.df

    def validate_input(self):
        """Perform input validation for required fields and record consistency."""
        if self.df is None:
            self.create_dataframe()

        if self.df.empty:
            raise ValueError("Dataset cannot be empty.")

        missing_required_columns = [
            column for column in self.REQUIRED_COLUMNS if column not in self.df.columns
        ]
        if missing_required_columns:
            raise ValueError(
                "Dataset is missing required columns: " + ", ".join(missing_required_columns)
            )

        return True

    def get_dataset_info(self):
        """Display dataset structure and metadata."""
        if self.df is None:
            self.create_dataframe()

        info = {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1],
            "column_names": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "shape": self.df.shape,
        }

        print("\n=== Dataset Information ===")
        print(f"Rows          : {info['rows']}")
        print(f"Columns       : {info['columns']}")
        print(f"Column Names  : {info['column_names']}")
        print(f"Dtypes        : {info['dtypes']}")
        print(f"Shape         : {info['shape']}")

        return info

    def find_missing_values(self):
        """Return the missing-value count for each column."""
        if self.df is None:
            self.create_dataframe()

        return self.df.isnull()

    def count_missing_values(self):
        """Return the total missing values count in the DataFrame."""
        if self.df is None:
            self.create_dataframe()

        missing_summary = self.df.isnull().sum()
        return missing_summary.to_dict()

    def find_duplicates(self):
        """Return the number of duplicate records in the dataset."""
        if self.df is None:
            self.create_dataframe()

        return int(self.df.duplicated().sum())

    def remove_duplicates(self):
        """Remove duplicate rows while preserving the original DataFrame."""
        if self.df is None:
            self.create_dataframe()

        self.cleaned_df = self.df.drop_duplicates(ignore_index=True).copy()
        return self.cleaned_df

    def fill_missing_values(self):
        """Fill missing Income values using mean imputation."""
        if self.cleaned_df is None:
            self.remove_duplicates()

        if "Income" not in self.cleaned_df.columns:
            raise ValueError("Income column is missing; cannot perform imputation.")

        income_mean = self.cleaned_df["Income"].mean()
        self.cleaned_df["Income"] = self.cleaned_df["Income"].fillna(income_mean)
        return self.cleaned_df

    def filter_customers(self, min_income):
        """Return customers whose Income is at least the given threshold."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        if not isinstance(min_income, (int, float)):
            raise TypeError("Minimum income must be numeric.")

        return self.cleaned_df[self.cleaned_df["Income"] >= min_income].copy()

    def sort_by_income(self, ascending=True):
        """Sort customers by income in ascending or descending order."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        return self.cleaned_df.sort_values(by="Income", ascending=ascending, ignore_index=True)

    def calculate_statistics(self):
        """Compute mean, minimum, maximum, and standard deviation for numeric features."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        numeric_columns = ["Age", "Income", "Experience", "Purchased"]
        stats = {}

        for column in numeric_columns:
            if column in self.cleaned_df.columns:
                series = pd.to_numeric(self.cleaned_df[column], errors="coerce")
                stats[column] = {
                    "mean": float(series.mean()),
                    "minimum": float(series.min()),
                    "maximum": float(series.max()),
                    "std_dev": float(series.std()),
                }

        return stats

    def analyze_features(self):
        """Display statistics for the numeric features in the cleaned dataset."""
        stats = self.calculate_statistics()
        print("\n=== Feature Statistics ===")
        for feature, values in stats.items():
            print(
                f"{feature}: Mean={values['mean']}, "
                f"Min={values['minimum']}, "
                f"Max={values['maximum']}, "
                f"Std Dev={values['std_dev']}"
            )
        return stats

    def analyze_target(self):
        """Count how many customers purchased and did not purchase."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        if "Purchased" not in self.cleaned_df.columns:
            raise ValueError("Purchased column is missing.")

        purchased_counts = self.cleaned_df["Purchased"].value_counts().sort_index()
        purchased = int(purchased_counts.get(1, 0))
        not_purchased = int(purchased_counts.get(0, 0))

        return {"Purchased": purchased, "Not Purchased": not_purchased}

    def perform_eda(self):
        """Run basic exploratory data analysis for the dataset."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        eda_report = {
            "customer_count": int(self.cleaned_df.shape[0]),
            "average_age": float(self.cleaned_df["Age"].mean()),
            "average_income": float(self.cleaned_df["Income"].mean()),
            "highest_income": float(self.cleaned_df["Income"].max()),
            "average_experience": float(self.cleaned_df["Experience"].mean()),
            "number_of_purchasers": int(self.cleaned_df["Purchased"].sum()),
        }

        print("\n=== Exploratory Data Analysis ===")
        print(f"Customer Count        : {eda_report['customer_count']}")
        print(f"Average Age           : {eda_report['average_age']}")
        print(f"Average Income        : {eda_report['average_income']}")
        print(f"Highest Income        : {eda_report['highest_income']}")
        print(f"Average Experience    : {eda_report['average_experience']}")
        print(f"Number of Purchasers  : {eda_report['number_of_purchasers']}")

        return eda_report

    def display_report(self):
        """Generate the full analysis report for the customer dataset."""
        if self.df is None:
            self.create_dataframe()

        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        duplicate_count = self.find_duplicates()
        missing_income = int(self.df["Income"].isnull().sum())
        rows_after_cleaning = self.cleaned_df.shape[0]
        stats = self.calculate_statistics()
        target_summary = self.analyze_target()
        eda_summary = self.perform_eda()

        print("\nCUSTOMER DATA ANALYSIS")
        print(f"Original Dataset Shape: {self.df.shape}")
        print(f"Missing Income Values: {missing_income}")
        print(f"Duplicate Records: {duplicate_count}")
        print(f"Rows After Cleaning: {rows_after_cleaning}")
        print("\nFeature Statistics:")

        for feature, values in stats.items():
            print(
                f"{feature}: Mean={values['mean']}, "
                f"Minimum={values['minimum']}, "
                f"Maximum={values['maximum']}, "
                f"Std Dev={values['std_dev']}"
            )

        print("\nPurchase Analysis:")
        print(f"Purchased: {target_summary['Purchased']}")
        print(f"Not Purchased: {target_summary['Not Purchased']}")

        report = {
            "original_shape": self.df.shape,
            "missing_income_values": missing_income,
            "duplicate_records": duplicate_count,
            "rows_after_cleaning": rows_after_cleaning,
            "feature_statistics": stats,
            "purchase_analysis": target_summary,
            "eda_summary": eda_summary,
        }
        return report

    def group_by_purchase_status(self):
        """Bonus challenge: summarize customers by purchase status."""
        if self.cleaned_df is None:
            self.remove_duplicates()
            self.fill_missing_values()

        grouped = (
            self.cleaned_df.groupby("Purchased")
            .agg(
                customer_count=("Customer", "count"),
                average_age=("Age", "mean"),
                average_income=("Income", "mean"),
                average_experience=("Experience", "mean"),
            )
            .reset_index()
        )
        return grouped


def run_test_cases():
    """Run the minimum seven test cases required by the exercise."""
    test_results = []

    def check(label, runner):
        try:
            runner()
            test_results.append((label, "PASS"))
            print(f"{label}: PASS")
        except Exception as error:
            test_results.append((label, f"FAIL: {error}"))
            print(f"{label}: FAIL -> {error}")

    # Test 1: Normal dataset
    def normal_dataset_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
            {"Customer": "C003", "Age": 35, "Income": None, "Experience": 8, "Purchased": 1},
            {"Customer": "C004", "Age": 40, "Income": 80000, "Experience": 12, "Purchased": 1},
            {"Customer": "C005", "Age": 45, "Income": 100000, "Experience": 15, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        analyzer.validate_input()
        analyzer.create_dataframe()
        assert analyzer.find_missing_values()["Income"].sum() == 1
        assert analyzer.find_duplicates() == 1
        analyzer.remove_duplicates()
        analyzer.fill_missing_values()
        assert analyzer.cleaned_df.shape[0] == 5
        assert analyzer.cleaned_df["Income"].isnull().sum() == 0
        filtered = analyzer.filter_customers(50000)
        assert filtered["Income"].ge(50000).all()

    check("Test Case 1 – Normal Dataset", normal_dataset_case)

    # Test 2: No missing values
    def no_missing_values_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        analyzer.create_dataframe()
        assert analyzer.count_missing_values() == {"Customer": 0, "Age": 0, "Income": 0, "Experience": 0, "Purchased": 0}

    check("Test Case 2 – No Missing Values", no_missing_values_case)

    # Test 3: Multiple missing values
    def multiple_missing_values_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Income": None, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
            {"Customer": "C003", "Age": 35, "Income": None, "Experience": 8, "Purchased": 1},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        analyzer.create_dataframe()
        assert analyzer.df["Income"].isnull().sum() == 2
        analyzer.remove_duplicates()
        analyzer.fill_missing_values()
        assert analyzer.cleaned_df["Income"].isnull().sum() == 0

    check("Test Case 3 – Multiple Missing Values", multiple_missing_values_case)

    # Test 4: Duplicate records
    def duplicate_records_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
            {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        analyzer.create_dataframe()
        assert analyzer.find_duplicates() == 1
        cleaned = analyzer.remove_duplicates()
        assert cleaned.shape[0] == 2

    check("Test Case 4 – Duplicate Records", duplicate_records_case)

    # Test 5: Missing required column
    def missing_required_column_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Experience": 5, "Purchased": 1},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        try:
            analyzer.validate_input()
            raise AssertionError("Expected a validation error for a missing required column.")
        except ValueError:
            pass

    check("Test Case 5 – Missing Required Column", missing_required_column_case)

    # Test 6: Empty dataset
    def empty_dataset_case():
        analyzer = PandasDataAnalyzer([])
        try:
            analyzer.validate_input()
            raise AssertionError("Expected an error for an empty dataset.")
        except (ValueError, TypeError):
            pass

    check("Test Case 6 – Empty Dataset", empty_dataset_case)

    # Test 7: Filtering
    def filtering_case():
        dataset = [
            {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
            {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
            {"Customer": "C003", "Age": 35, "Income": 60000, "Experience": 8, "Purchased": 1},
        ]
        analyzer = PandasDataAnalyzer(dataset)
        filtered = analyzer.filter_customers(50000)
        assert filtered["Income"].ge(50000).all()

    check("Test Case 7 – Filtering", filtering_case)

    return test_results


def main():
    """Workflow orchestration for the Pandas data cleaning and EDA task."""
    data = [
        {"Customer": "C001", "Age": 25, "Income": 30000, "Experience": 2, "Purchased": 0},
        {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
        {"Customer": "C003", "Age": 35, "Income": None, "Experience": 8, "Purchased": 1},
        {"Customer": "C004", "Age": 40, "Income": 80000, "Experience": 12, "Purchased": 1},
        {"Customer": "C005", "Age": 45, "Income": 100000, "Experience": 15, "Purchased": 0},
        {"Customer": "C002", "Age": 30, "Income": 45000, "Experience": 5, "Purchased": 1},
    ]

    try:
        analyzer = PandasDataAnalyzer(data)
        analyzer.create_dataframe()
        analyzer.validate_input()
        analyzer.get_dataset_info()
        print("\nMissing Values:\n", analyzer.find_missing_values())
        print(f"Duplicate Records: {analyzer.find_duplicates()}")
        analyzer.remove_duplicates()
        analyzer.fill_missing_values()
        print("\nCleaned DataFrame:\n", analyzer.cleaned_df)
        print("\nFilter (Income >= 50000):\n", analyzer.filter_customers(50000))
        print("\nSorted by Income (Descending):\n", analyzer.sort_by_income(ascending=False))
        analyzer.analyze_features()
        analyzer.perform_eda()
        print("\nTarget Analysis:", analyzer.analyze_target())
        print("\nGroup by Purchase Status:\n", analyzer.group_by_purchase_status())
        analyzer.display_report()
        print("\n=== Automated Test Cases ===")
        run_test_cases()
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
