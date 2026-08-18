"""
NumPy-Based Feature Processing Module
=====================================
Task ID: ML-NP-007
Difficulty: Intermediate + 5%

This module implements a NumpyFeatureProcessor class that provides
efficient numerical data processing and transformation using NumPy.

Key Features:
- Array conversion and introspection
- Statistical calculations (min, max, mean, std)
- Min-Max Scaling (normalization)
- Z-Score Standardization
- Comprehensive error handling
- Vectorized numerical operations

Author: Data Science Team
Date: 2026
"""

import numpy as np


class NumpyFeatureProcessor:
    """
    A class for processing numerical data using NumPy.
    
    Attributes:
        data (list): Original Python list of numerical values
        array (np.ndarray): NumPy array representation of data
        min_max_data (np.ndarray): Min-Max scaled data
        standardized_data (np.ndarray): Z-Score standardized data
    
    Methods:
        validate_input(): Validates input data
        convert_to_array(): Converts Python list to NumPy array
        get_array_info(): Displays array properties
        calculate_minimum(): Returns minimum value
        calculate_maximum(): Returns maximum value
        calculate_mean(): Returns mean value
        calculate_standard_deviation(): Returns standard deviation
        min_max_scale(): Performs Min-Max Scaling
        standardize(): Performs Z-Score Standardization
        compare_scaling_methods(): Displays comparison table (bonus)
        display_report(): Generates comprehensive processing report
    """
    
    def __init__(self, data):
        """
        Initialize the NumpyFeatureProcessor.
        
        Args:
            data (list): List of numerical values to process
        
        Raises:
            TypeError: If data is not a list
            ValueError: If data is empty or contains non-numeric values
        """
        self.data = data
        self.array = None
        self.min_max_data = None
        self.standardized_data = None
        self.statistics = {}
        
        # Validate and process input
        self.validate_input()
        self.convert_to_array()
        self._calculate_statistics()
    
    def validate_input(self):
        """
        Validate input data.
        
        Checks:
        - Data is not None and is a list
        - Data is not empty
        - All elements are numerical (int, float)
        
        Raises:
            TypeError: If data is not a list
            ValueError: If data is empty or contains non-numeric values
        """
        if not isinstance(self.data, list):
            raise TypeError(f"Input must be a list. Received: {type(self.data).__name__}")
        
        if len(self.data) == 0:
            raise ValueError("Input list cannot be empty.")
        
        for idx, value in enumerate(self.data):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(
                    f"Dataset contains non-numeric values. "
                    f"Position {idx}: {value} (type: {type(value).__name__})"
                )
    
    def convert_to_array(self):
        """
        Convert Python list to NumPy array.
        
        Uses np.array() to create an ndarray from self.data.
        Stores result in self.array.
        """
        try:
            self.array = np.array(self.data)
        except Exception as e:
            raise RuntimeError(f"Failed to convert data to NumPy array: {str(e)}")
    
    def get_array_info(self):
        """
        Get detailed information about the NumPy array.
        
        Returns:
            dict: Dictionary containing:
                - array: The actual array
                - dtype: Data type
                - ndim: Number of dimensions
                - shape: Shape tuple
                - size: Total number of elements
        """
        return {
            'array': self.array,
            'dtype': self.array.dtype,
            'ndim': self.array.ndim,
            'shape': self.array.shape,
            'size': self.array.size
        }
    
    def calculate_minimum(self):
        """
        Calculate the minimum value using NumPy.
        
        Returns:
            float/int: Minimum value in the array
        """
        return float(np.min(self.array))
    
    def calculate_maximum(self):
        """
        Calculate the maximum value using NumPy.
        
        Returns:
            float/int: Maximum value in the array
        """
        return float(np.max(self.array))
    
    def calculate_mean(self):
        """
        Calculate the mean (average) value using NumPy.
        
        Returns:
            float: Mean value of the array
        """
        return float(np.mean(self.array))
    
    def calculate_standard_deviation(self):
        """
        Calculate the standard deviation using NumPy.
        
        Returns:
            float: Standard deviation of the array
        
        Note:
            Uses NumPy's default (population standard deviation).
        """
        return float(np.std(self.array))
    
    def _calculate_statistics(self):
        """
        Calculate and cache all statistics.
        
        Stores minimum, maximum, mean, and standard deviation
        in self.statistics dictionary for efficient access.
        """
        self.statistics = {
            'minimum': self.calculate_minimum(),
            'maximum': self.calculate_maximum(),
            'mean': self.calculate_mean(),
            'std': self.calculate_standard_deviation()
        }
    
    def min_max_scale(self):
        """
        Perform Min-Max Scaling (Normalization).
        
        Transforms data to range [0, 1] using formula:
        scaled_value = (value - min) / (max - min)
        
        Returns:
            np.ndarray: Scaled array in range [0, 1]
        
        Raises:
            ValueError: If all values are identical (range is 0)
        """
        min_val = self.statistics['minimum']
        max_val = self.statistics['maximum']
        
        # Check for constant dataset
        if min_val == max_val:
            raise ValueError(
                "Cannot perform Min-Max scaling: all values are identical. "
                f"Constant value: {min_val}. Range is zero."
            )
        
        # Vectorized Min-Max scaling
        self.min_max_data = (self.array - min_val) / (max_val - min_val)
        return self.min_max_data
    
    def standardize(self):
        """
        Perform Z-Score Standardization.
        
        Transforms data to have mean=0 and std=1 using formula:
        standardized_value = (value - mean) / std
        
        Returns:
            np.ndarray: Standardized array
        
        Raises:
            ValueError: If standard deviation is zero
        """
        mean_val = self.statistics['mean']
        std_val = self.statistics['std']
        
        # Check for zero standard deviation
        if std_val == 0:
            raise ValueError(
                "Cannot perform Z-Score standardization: standard deviation is zero. "
                "This occurs when all values are identical."
            )
        
        # Vectorized Z-Score standardization
        self.standardized_data = (self.array - mean_val) / std_val
        return self.standardized_data
    
    def compare_scaling_methods(self):
        """
        Bonus Challenge: Compare scaling methods side-by-side.
        
        Displays a table with Original, Min-Max, and Z-Score values.
        Provides analysis of both transformation methods.
        """
        # Perform scaling if not already done
        try:
            min_max = self.min_max_scale() if self.min_max_data is None else self.min_max_data
        except ValueError as e:
            print(f"\n[WARN]  Cannot compute Min-Max: {e}")
            min_max = None
        
        try:
            standardized = self.standardize() if self.standardized_data is None else self.standardized_data
        except ValueError as e:
            print(f"\n[WARN]  Cannot compute Standardization: {e}")
            standardized = None
        
        # Display comparison table
        print("\n" + "="*80)
        print("SCALING METHODS COMPARISON TABLE")
        print("="*80)
        print(f"{'Index':<8} {'Original':<15} {'Min-Max (0-1)':<20} {'Z-Score':<15}")
        print("-"*80)
        
        for idx, original_val in enumerate(self.array):
            min_max_val = f"{min_max[idx]:.4f}" if min_max is not None else "N/A"
            z_score_val = f"{standardized[idx]:.4f}" if standardized is not None else "N/A"
            print(f"{idx:<8} {float(original_val):<15.4f} {min_max_val:<20} {z_score_val:<15}")
        
        print("="*80)
        
        # Analysis and Explanation
        print("\n[CHART] SCALING METHODS ANALYSIS:")
        print("-"*80)
        print("\n(1)  Which transformation produces values between 0 and 1?")
        print("   [OK] Min-Max Scaling (Normalization)")
        print("   - Formula: (value - min) / (max - min)")
        print("   - Range: [0, 1]")
        print("   - Use case: When you need bounded values (neural networks, probabilities)")
        
        print("\n(2)  Which transformation produces values centered around zero?")
        print("   [OK] Z-Score Standardization")
        print("   - Formula: (value - mean) / std")
        print("   - Mean: ~0, Std: ~1")
        print("   - Use case: When features should have similar scales (linear regression, SVM)")
        
        print("\n(3)  What happens to the mean after standardization?")
        if standardized is not None:
            print(f"   [OK] Mean becomes ~ 0 (actual: {np.mean(standardized):.10f})")
            print(f"   [OK] Standard Deviation becomes ~ 1 (actual: {np.std(standardized):.10f})")
        else:
            print("   [OK] Cannot calculate (constant dataset)")
        
        print("\n(4)  Why might an ML algorithm benefit from either transformation?")
        print("   [OK] Min-Max Scaling:")
        print("     - Preserves the distribution shape")
        print("     - Bounded output useful for activation functions")
        print("     - Sensitive to outliers")
        print("   [OK] Z-Score Standardization:")
        print("     - Makes features comparable on same scale")
        print("     - Reduces impact of outliers (relative to scale)")
        print("     - Naturally centered at zero")
        print("     - Better for algorithms assuming normally distributed data")
        print("="*80 + "\n")
    
    def display_report(self):
        """
        Display comprehensive processing report.
        
        Shows:
        - Original data
        - NumPy array and its properties
        - Statistical calculations
        - Min-Max scaled data
        - Z-Score standardized data
        
        Handles edge cases gracefully.
        """
        print("\n" + "="*80)
        print(" "*20 + "NUMPY FEATURE PROCESSING REPORT")
        print("="*80)
        
        # Original Data
        print("\n[DATA] Original Data:")
        print(f"   {self.data}")
        
        # NumPy Array Information
        print("\n[CHART] NumPy Array:")
        array_info = self.get_array_info()
        print(f"   {array_info['array']}")
        print(f"\n   Data Type: {array_info['dtype']}")
        print(f"   Dimensions: {array_info['ndim']}")
        print(f"   Shape: {array_info['shape']}")
        print(f"   Size: {array_info['size']}")
        
        # Statistics
        print("\n[STATS] Statistical Analysis:")
        print(f"   Minimum:           {self.statistics['minimum']}")
        print(f"   Maximum:           {self.statistics['maximum']}")
        print(f"   Mean:              {self.statistics['mean']:.4f}")
        print(f"   Std Deviation:     {self.statistics['std']:.4f}")
        
        # Min-Max Scaling
        print("\n[TRANSFORM] Min-Max Scaling (0-1 Range):")
        try:
            min_max_result = self.min_max_scale()
            formatted = [f"{val:.2f}" for val in min_max_result]
            print(f"   [{', '.join(formatted)}]")
        except ValueError as e:
            print(f"   [FAIL] Error: {e}")
        
        # Z-Score Standardization
        print("\n[POINT] Z-Score Standardization (Mean~0, Std~1):")
        try:
            std_result = self.standardize()
            formatted = [f"{val:.4f}" for val in std_result]
            print(f"   [{', '.join(formatted)}]")
        except ValueError as e:
            print(f"   [FAIL] Error: {e}")
        
        print("\n" + "="*80 + "\n")


def test_case_1():
    """Test Case 1: Normal Dataset"""
    print("\n[TEST] TEST CASE 1: Normal Dataset [10, 20, 30, 40, 50]")
    print("-"*80)
    try:
        data = [10, 20, 30, 40, 50]
        processor = NumpyFeatureProcessor(data)
        processor.display_report()
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_case_2():
    """Test Case 2: Negative Values"""
    print("\n[TEST] TEST CASE 2: Negative Values [-10, -5, 0, 5, 10]")
    print("-"*80)
    try:
        data = [-10, -5, 0, 5, 10]
        processor = NumpyFeatureProcessor(data)
        processor.display_report()
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_case_3():
    """Test Case 3: Decimal Values"""
    print("\n[TEST] TEST CASE 3: Decimal Values [1.5, 2.5, 3.5, 4.5]")
    print("-"*80)
    try:
        data = [1.5, 2.5, 3.5, 4.5]
        processor = NumpyFeatureProcessor(data)
        processor.display_report()
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_case_4():
    """Test Case 4: Constant Dataset (Expected to Fail)"""
    print("\n[TEST] TEST CASE 4: Constant Dataset [100, 100, 100]")
    print("-"*80)
    print("Expected: Error due to zero standard deviation when scaling/standardizing")
    try:
        data = [100, 100, 100]
        processor = NumpyFeatureProcessor(data)
        
        # Try to scale - should raise an error
        error_caught = False
        try:
            processor.min_max_scale()
        except ValueError as e:
            print(f"[OK] Correctly caught Min-Max error: {e}")
            error_caught = True
        
        if not error_caught:
            print("[FAIL] Should have raised an error for Min-Max scaling!")
            return False
        
        # Try to standardize - should raise an error
        error_caught = False
        try:
            processor.standardize()
        except ValueError as e:
            print(f"[OK] Correctly caught Standardization error: {e}")
            error_caught = True
        
        if not error_caught:
            print("[FAIL] Should have raised an error for standardization!")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def test_case_5():
    """Test Case 5: Invalid Dataset (Non-numeric)"""
    print("\n[TEST] TEST CASE 5: Invalid Dataset [10, 20, '30', 40]")
    print("-"*80)
    print("Expected: Error due to non-numeric value")
    try:
        data = [10, 20, "30", 40]
        processor = NumpyFeatureProcessor(data)
        print("[FAIL] Should have raised an error!")
        return False
    except ValueError as e:
        print(f"[OK] Correctly caught error: {e}")
        return True


def test_case_6():
    """Test Case 6: Empty Dataset"""
    print("\n[TEST] TEST CASE 6: Empty Dataset []")
    print("-"*80)
    print("Expected: Error due to empty input")
    try:
        data = []
        processor = NumpyFeatureProcessor(data)
        print("[FAIL] Should have raised an error!")
        return False
    except ValueError as e:
        print(f"[OK] Correctly caught error: {e}")
        return True


def main():
    """
    Main function to execute all test cases and demonstrate functionality.
    """
    print("\n" + "="*80)
    print(" "*15 + "NUMPY FEATURE PROCESSOR - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"NumPy Version: {np.__version__}")
    print("="*80)
    
    # Run all test cases
    test_results = []
    test_results.append(("Test 1: Normal Dataset", test_case_1()))
    test_results.append(("Test 2: Negative Values", test_case_2()))
    test_results.append(("Test 3: Decimal Values", test_case_3()))
    test_results.append(("Test 4: Constant Dataset", test_case_4()))
    test_results.append(("Test 5: Invalid Dataset", test_case_5()))
    test_results.append(("Test 6: Empty Dataset", test_case_6()))
    
    # Bonus: Scaling comparison (using Test 1 data)
    print("\n" + "="*80)
    print(" "*20 + "BONUS CHALLENGE: SCALING METHODS COMPARISON")
    print("="*80)
    try:
        data = [10, 20, 30, 40, 50]
        processor = NumpyFeatureProcessor(data)
        processor.compare_scaling_methods()
    except Exception as e:
        print(f"[FAIL] Error in bonus challenge: {e}")
    
    # Test Summary
    print("\n" + "="*80)
    print(" "*25 + "TEST SUMMARY")
    print("="*80)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    print(f"\n{'Test Case':<30} {'Status':<20}")
    print("-"*80)
    for test_name, result in test_results:
        status = "[OK] PASSED" if result else "[FAIL] FAILED"
        print(f"{test_name:<30} {status:<20}")
    
    print("-"*80)
    print(f"Total: {passed}/{total} tests passed")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
