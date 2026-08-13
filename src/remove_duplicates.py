class RemoveDuplicates:
	def __init__(self, numbers):
		"""Initialize the RemoveDuplicates instance with a list of numbers.

		Args:
			numbers (list): The list of numbers to process.
		"""
		# Store the input list for later processing
		self.numbers = numbers

	def validate_input(self):
		"""Validate that the input is a list.

		Raises:
			TypeError: If `self.numbers` is not a list.
		"""
		# Ensure the provided input is a list before processing it
		if not isinstance(self.numbers, list):
			raise TypeError('Input must be a list.')

	def remove_duplicates(self):
		"""Return a list of unique numbers preserving original order."""
		# Create a new list to hold only the first occurrence of each value
		unique_numbers = []
		for value in self.numbers:
			if value not in unique_numbers:
				unique_numbers.append(value)
		return unique_numbers

	def display_result(self):
		"""Print the original list and the list with duplicates removed."""
		# Get the unique values and show them to the user
		unique = self.remove_duplicates()
		print("Original List : {}".format(self.numbers))
		print()
		print("Unique List   : {}".format(unique))


def main():
	# Sample data used to demonstrate the program
	numbers = [10, 20, 10, 30, 40, 20, 50, 30]
	rd = RemoveDuplicates(numbers)
	try:
		# Validate the input before showing the result
		rd.validate_input()
		rd.display_result()
	except Exception as e:
		print("Error:", e)


if __name__ == '__main__':
	main()

