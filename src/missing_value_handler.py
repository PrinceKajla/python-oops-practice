class MissingValueHandler:
    def __init__(self, data):
        self.data = data.copy()
        self.cleaned_data = None

    def validate_data(self):
            raise ValueError("Input list cannot be empty.")

        if not isinstance(self.data, list):
            raise TypeError("Input must be a list.")

        if len(self.data) == 0:
        for value in self.data:
            if value is not None and not isinstance(value, (int, float)):
                raise TypeError("Dataset contains invalid values.")

    def find_missing_indexes(self):
        missing_indexes = []

        for index in range(len(self.data)):
            if self.data[index] is None:
                missing_indexes.append(index)

        return missing_indexes

    def count_missing(self):
        return len(self.find_missing_indexes())

    def get_available_values(self):
        available_values = []

        for value in self.data:
            if value is not None:
                available_values.append(value)

        return available_values

    def calculate_mean(self):
        available_values = self.get_available_values()

        if len(available_values) == 0:
            raise ValueError(
                "No valid values exist to calculate the mean."
            )

        total = 0

        for value in available_values:
            total += value

        mean = total / len(available_values)

        return mean

    def fill_with_mean(self):
        mean = self.calculate_mean()

        cleaned_data = self.data.copy()

        for index in range(len(cleaned_data)):
            if cleaned_data[index] is None:
                cleaned_data[index] = mean

        self.cleaned_data = cleaned_data

        return cleaned_data

    def fill_with_median(self):
        available_values = self.get_available_values()

        if len(available_values) == 0:
            raise ValueError(
                "No valid values exist to calculate the median."
            )

        sorted_values = sorted(available_values)

        n = len(sorted_values)

        if n % 2 == 1:
            median = sorted_values[n // 2]
        else:
            middle1 = sorted_values[(n // 2) - 1]
            middle2 = sorted_values[n // 2]

            median = (middle1 + middle2) / 2

        cleaned_data = self.data.copy()

        for index in range(len(cleaned_data)):
            if cleaned_data[index] is None:
                cleaned_data[index] = median

        self.cleaned_data = cleaned_data

        return cleaned_data

    def fill_with_zero(self):
        cleaned_data = self.data.copy()

        for index in range(len(cleaned_data)):
            if cleaned_data[index] is None:
                cleaned_data[index] = 0

        self.cleaned_data = cleaned_data

        return cleaned_data

    def fill_missing_values(self, strategy):
        strategy = strategy.lower()

        if strategy == "mean":
            return self.fill_with_mean()

        elif strategy == "median":
            return self.fill_with_median()

        elif strategy == "zero":
            return self.fill_with_zero()

        else:
            raise ValueError(
                "Invalid strategy. Use 'mean', 'median', or 'zero'."
            )

    def display_report(self):
        self.validate_data()

        missing_indexes = self.find_missing_indexes()
        missing_count = len(missing_indexes)
        available_values = self.get_available_values()

        print("\n" + "=" * 40)
        print("        MISSING VALUE REPORT")
        print("=" * 40)

        print("\nOriginal Data:")
        print(self.data)

        print(f"\nTotal Values       : {len(self.data)}")
        print(f"Missing Values     : {missing_count}")
        print(f"Missing Indexes    : {missing_indexes}")
        print(f"Available Values   : {len(available_values)}")

        if missing_count > 0:
            mean = self.calculate_mean()
            print(f"Mean               : {mean}")

            self.cleaned_data = self.fill_with_mean()

            print("\nCleaned Data:")
            print(self.cleaned_data)

        else:
            print("\nMean               : No missing values")
            print("\nCleaned Data:")
            print(self.data.copy())

        print("\n" + "=" * 40)

def main():
    data = [25, 30, None, 40, None, 35, 28]

    try:
        handler = MissingValueHandler(data)
        handler.display_report()

    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()