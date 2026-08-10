class StatisticalAnalyzer:
    def __init__(self, data):
        self.data = data

    def mean(self):
        return sum(self.data) / len(self.data)

    def median(self):
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]

    def variance(self):
        mean_value = self.mean()
        return sum((x - mean_value) ** 2 for x in self.data) / len(self.data)

    def standard_deviation(self):
        return self.variance() ** 0.5