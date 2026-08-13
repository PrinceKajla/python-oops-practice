class StatisticalAnalyzer:
    def __init__(self, numbers):
        self.numbers = numbers

    def validate_input(self):
        if not isinstance(self.numbers, list):
            raise TypeError("Input must be a list of numerical values.")

        if len(self.numbers) == 0:
            raise ValueError("Input list cannot be empty.")

        for item in self.numbers:
            if not isinstance(item, (int, float)):
                raise TypeError("Input must contain only numerical values.")

    def calculate_mean(self):
        total = 0
        count = len(self.numbers)
        for value in self.numbers:
            total += value
        return total / count

    def calculate_median(self):
        sorted_numbers = sorted(self.numbers)
        n = len(sorted_numbers)
        mid = n // 2

        if n % 2 == 0:
            return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
        return sorted_numbers[mid]

    def calculate_mode(self):
        frequency = {}
        for value in self.numbers:
            frequency[value] = frequency.get(value, 0) + 1

        highest_count = max(frequency.values())
        if highest_count == 1:
            return "No unique mode"

        modes = [value for value, count in frequency.items() if count == highest_count]
        if len(modes) == 1:
            return modes[0]
        return sorted(modes)

    def find_minimum(self):
        smallest = self.numbers[0]
        for value in self.numbers[1:]:
            if value < smallest:
                smallest = value
        return smallest

    def find_maximum(self):
        largest = self.numbers[0]
        for value in self.numbers[1:]:
            if value > largest:
                largest = value
        return largest

    def count_unique_values(self):
        unique_values = set(self.numbers)
        return len(unique_values)

    def calculate_range(self):
        return self.find_maximum() - self.find_minimum()

    def calculate_variance(self):
        mean_value = self.calculate_mean()
        squared_differences = 0
        for value in self.numbers:
            squared_differences += (value - mean_value) ** 2
        return squared_differences / len(self.numbers)

    def display_result(self):
        mean_value = self.calculate_mean()
        median_value = self.calculate_median()
        mode_value = self.calculate_mode()
        minimum_value = self.find_minimum()
        maximum_value = self.find_maximum()
        unique_count = self.count_unique_values()
        range_value = self.calculate_range()
        variance_value = self.calculate_variance()

        print("================================")
        print("       STATISTICAL REPORT")
        print("================================")
        print(f"Original Data : {self.numbers}")
        print(f"\nMean          : {mean_value:.2f}")
        print(f"Median        : {median_value}")
        print(f"Mode          : {mode_value}")
        print(f"Minimum       : {minimum_value}")
        print(f"Maximum       : {maximum_value}")
        print(f"Unique Values : {unique_count}")
        print(f"Range         : {range_value}")
        print(f"Variance      : {variance_value:.2f}")
        print("================================")


def main():
    numbers = [10, 20, 20, 30, 40, 50]
    analyzer = StatisticalAnalyzer(numbers)

    try:
        analyzer.validate_input()
        analyzer.display_result()
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == '__main__':
    main()
