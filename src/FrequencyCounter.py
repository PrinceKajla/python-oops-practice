# frequency_counter.py

class FrequencyCounter:
    def __init__(self, numbers):
        self.numbers = numbers

    def validate_input(self):
        if not isinstance(self.numbers, list):
            raise TypeError("Input must be a list.")
        if len(self.numbers) == 0:
            raise ValueError("Input list cannot be empty.")

    def count_frequency(self):
        frequency = {}

        for item in self.numbers:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1

        return frequency

    def display_result(self):
        frequency = self.count_frequency()

        print("Frequency Dictionary:")
        print(frequency)

        # Bonus Challenge
        sorted_frequency = dict(sorted(frequency.items()))
        print("\nSorted Frequency Dictionary:")
        print(sorted_frequency)

        max_count = max(frequency.values())
        min_count = min(frequency.values())

        most_frequent = [k for k, v in frequency.items() if v == max_count]
        least_frequent = [k for k, v in frequency.items() if v == min_count]

        print("\nMost Frequent Element(s):", most_frequent)
        print("Least Frequent Element(s):", least_frequent)

        unique_elements = sum(1 for v in frequency.values() if v == 1)
        duplicate_elements = sum(1 for v in frequency.values() if v > 1)

        print("Unique Elements:", unique_elements)
        print("Duplicate Elements:", duplicate_elements)


def main():
    try:
        numbers = [1, 2, 2, 3, 1, 5, 4, 2, 5, 5]

        counter = FrequencyCounter(numbers)

        counter.validate_input()
        counter.display_result()

    except (TypeError, ValueError) as e:
        print("Error:", e)


if __name__ == "__main__":
    main()