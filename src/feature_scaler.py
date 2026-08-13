class FeatureScaler:
    """Scale numerical data using Min-Max normalization.

    Formula for standard range [0, 1]:
        scaled = (value - minimum) / (maximum - minimum)

    For a custom target range [new_min, new_max]:
        scaled = ((value - minimum) / (maximum - minimum)) * (new_max - new_min) + new_min
    """

    def __init__(self, data, new_min=0, new_max=1):
        self.data = data.copy() if isinstance(data, list) else data
        self.new_min = new_min
        self.new_max = new_max
        self.scaled_data = []

    def validate_input(self):
        """Validate that the input list is non-empty and contains only numeric values."""
        if not isinstance(self.data, list):
            raise TypeError("Input must be a list.")

        if len(self.data) == 0:
            raise ValueError("Input list cannot be empty.")

        for value in self.data:
            if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("Dataset contains invalid values.")

    def find_minimum(self):
        self.validate_input()
        minimum = self.data[0]

        for value in self.data[1:]:
            if value < minimum:
                minimum = value

        return minimum

    def find_maximum(self):
        self.validate_input()
        maximum = self.data[0]

        for value in self.data[1:]:
            if value > maximum:
                maximum = value

        return maximum

    def scale_data(self):
        self.validate_input()

        minimum = self.find_minimum()
        maximum = self.find_maximum()

        if minimum == maximum:
            raise ValueError("Cannot scale data because all values are identical.")

        scaled_values = []
        range_size = maximum - minimum

        for value in self.data:
            normalized = (value - minimum) / range_size
            scaled_value = normalized * (self.new_max - self.new_min) + self.new_min
            scaled_values.append(scaled_value)

        self.scaled_data = scaled_values
        return self.scaled_data

    def display_report(self):
        self.validate_input()

        minimum = self.find_minimum()
        maximum = self.find_maximum()

        if not self.scaled_data:
            self.scale_data()

        print("========================================")
        print("          FEATURE SCALING REPORT")
        print("========================================")
        print(f"Original Data : {self.data}")
        print(f"Minimum       : {minimum}")
        print(f"Maximum       : {maximum}")
        print(f"Scaled Data   : {self.scaled_data}")
        print("========================================")

        return {
            "original_data": self.data.copy(),
            "minimum": minimum,
            "maximum": maximum,
            "scaled_data": self.scaled_data.copy(),
        }


def main():
    data = [10, 20, 30, 40, 50]

    try:
        obj = FeatureScaler(data)
        obj.validate_input()
        obj.display_report()
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
