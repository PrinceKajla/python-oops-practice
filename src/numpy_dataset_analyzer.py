import numpy as np


class NumpyDatasetAnalyzer:
    """Analyze a 2D numerical dataset using NumPy operations."""

    def __init__(self, data):
        self.data = data
        self.array = None

    def validate_input(self):
        """Validate that the dataset is a non-empty 2D list of numeric values."""
        if not isinstance(self.data, list):
            raise TypeError("Dataset must be a Python list of rows.")

        if len(self.data) == 0:
            raise ValueError("Dataset cannot be empty.")

        if not all(isinstance(row, (list, tuple, np.ndarray)) for row in self.data):
            raise TypeError("Each row must be a list-like collection of values.")

        if any(len(row) == 0 for row in self.data):
            raise ValueError("Each row must contain values.")

        expected_columns = len(self.data[0])

        for row_index, row in enumerate(self.data):
            if len(row) != expected_columns:
                raise ValueError(
                    f"All rows must contain the same number of columns. Row {row_index} has {len(row)} values, expected {expected_columns}."
                )

            for value in row:
                if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
                    raise TypeError("Dataset contains non-numeric values.")

        return True

    def convert_to_array(self):
        """Convert the validated dataset to a 2D NumPy array."""
        self.validate_input()
        self.array = np.asarray(self.data, dtype=float)
        return self.array

    def get_dataset_info(self):
        """Return dataset metadata including size and dimensionality."""
        if self.array is None:
            self.convert_to_array()

        info = {
            "rows": self.array.shape[0],
            "columns": self.array.shape[1],
            "dimensions": self.array.ndim,
            "size": self.array.size,
            "dtype": str(self.array.dtype),
        }

        print("\n=== Dataset Information ===")
        print(f"Rows       : {info['rows']}")
        print(f"Columns    : {info['columns']}")
        print(f"Dimensions : {info['dimensions']}")
        print(f"Size       : {info['size']}")
        print(f"Data Type  : {info['dtype']}")

        return info

    def get_column(self, column_index):
        """Return a NumPy column selected by index."""
        if self.array is None:
            self.convert_to_array()

        if not 0 <= column_index < self.array.shape[1]:
            raise IndexError("Column index is out of range.")

        return self.array[:, column_index]

    def get_row(self, row_index):
        """Return a NumPy row selected by index."""
        if self.array is None:
            self.convert_to_array()

        if not 0 <= row_index < self.array.shape[0]:
            raise IndexError("Row index is out of range.")

        return self.array[row_index, :]

    def calculate_column_mean(self):
        """Compute the mean for each feature (axis=0)."""
        if self.array is None:
            self.convert_to_array()

        return np.mean(self.array, axis=0)

    def calculate_column_minimum(self):
        """Compute the minimum value for each feature (axis=0)."""
        if self.array is None:
            self.convert_to_array()

        return np.min(self.array, axis=0)

    def calculate_column_maximum(self):
        """Compute the maximum value for each feature (axis=0)."""
        if self.array is None:
            self.convert_to_array()

        return np.max(self.array, axis=0)

    def calculate_column_std(self):
        """Compute the standard deviation for each feature (axis=0)."""
        if self.array is None:
            self.convert_to_array()

        return np.std(self.array, axis=0)

    def scale_features(self):
        """Apply independent Min-Max scaling to each feature column."""
        if self.array is None:
            self.convert_to_array()

        scaled_array = self.array.copy().astype(float)

        for column_index in range(self.array.shape[1]):
            column = scaled_array[:, column_index]
            minimum = np.min(column)
            maximum = np.max(column)

            if maximum == minimum:
                scaled_array[:, column_index] = 0.0
            else:
                scaled_array[:, column_index] = (column - minimum) / (maximum - minimum)

        return scaled_array

    def feature_summary(self):
        """Summarize mean, minimum, maximum, and standard deviation for each feature."""
        if self.array is None:
            self.convert_to_array()

        means = self.calculate_column_mean()
        minima = self.calculate_column_minimum()
        maxima = self.calculate_column_maximum()
        stds = self.calculate_column_std()

        summary = {}
        print("\n=== Feature Summary ===")

        for i in range(self.array.shape[1]):
            feature_key = f"Feature {i + 1}"
            feature_stats = {
                "mean": float(means[i]),
                "minimum": float(minima[i]),
                "maximum": float(maxima[i]),
                "std": float(stds[i]),
            }
            summary[feature_key] = feature_stats
            print(f"{feature_key}: mean={feature_stats['mean']}, min={feature_stats['minimum']}, max={feature_stats['maximum']}, std={feature_stats['std']}")

        return summary

    def display_report(self):
        """Print a complete analysis of the dataset."""
        if self.array is None:
            self.convert_to_array()

        info = self.get_dataset_info()
        print("\nSelected Row 1:", self.get_row(0))
        print("Selected Column 1:", self.get_column(0))
        print("\nColumn Means:", self.calculate_column_mean())
        print("Column Minimums:", self.calculate_column_minimum())
        print("Column Maximums:", self.calculate_column_maximum())
        print("Column Std Dev:", self.calculate_column_std())
        print("\nScaled Features:\n", self.scale_features())

        feature_summary = self.feature_summary()

        report = {
            "dataset_info": info,
            "row_0": self.get_row(0).tolist(),
            "column_0": self.get_column(0).tolist(),
            "column_means": self.calculate_column_mean().tolist(),
            "column_minimums": self.calculate_column_minimum().tolist(),
            "column_maximums": self.calculate_column_maximum().tolist(),
            "column_std": self.calculate_column_std().tolist(),
            "scaled_features": self.scale_features().tolist(),
            "feature_summary": feature_summary,
        }

        return report

    def split_features_target(self, target_index):
        """Split the array into feature matrix X and target vector y."""
        if self.array is None:
            self.convert_to_array()

        if target_index < 0 or target_index >= self.array.shape[1]:
            raise IndexError("Target index is out of range for the available columns.")

        X = np.delete(self.array, target_index, axis=1)
        y = self.array[:, target_index]
        return X, y


def run_required_test_cases():
    """Exercise the six required scenarios and validate the expected behavior."""
    test_cases = [
        ("Normal Dataset", [[25, 30000, 2], [30, 45000, 5], [35, 60000, 8]], None),
        ("Single Row", [[25, 30000, 2]], None),
        ("Unequal Columns", [[25, 30000], [30, 45000, 5]], "All rows must contain the same number of columns."),
        ("Invalid Data", [[25, 30000, 2], [30, "45000", 5]], "Dataset contains non-numeric values."),
        ("Empty Dataset", [], "Dataset cannot be empty."),
        ("Constant Feature", [[25, 30000, 5], [30, 45000, 5], [35, 60000, 5]], None),
    ]

    results = []

    for name, dataset, expected_error in test_cases:
        try:
            analyzer = NumpyDatasetAnalyzer(dataset)
            analyzer.validate_input()
            analyzer.convert_to_array()
            if expected_error is not None:
                raise AssertionError(f"{name}: Expected an error but validation succeeded.")
            results.append((name, "PASS"))
            print(f"{name}: PASS")
        except Exception as error:
            if expected_error is not None and str(error).startswith(expected_error[:10]):
                results.append((name, "PASS (expected error)"))
                print(f"{name}: PASS (expected error: {error})")
            else:
                results.append((name, f"FAIL: {error}"))
                print(f"{name}: FAIL -> {error}")

    return results


def main():
    """Run the sample dataset analysis and required validation tests."""
    sample_dataset = [[25, 30000, 2], [30, 45000, 5], [35, 60000, 8], [40, 80000, 12], [45, 100000, 15]]

    print("=== Required Test Cases ===")
    run_required_test_cases()

    print("\n=== Sample Dataset Analysis ===")
    try:
        analyzer = NumpyDatasetAnalyzer(sample_dataset)
        analyzer.display_report()
        print("\nSplit Example (target in final column):")
        X, y = analyzer.split_features_target(target_index=2)
        print("X =", X)
        print("y =", y)
    except (TypeError, ValueError, IndexError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
