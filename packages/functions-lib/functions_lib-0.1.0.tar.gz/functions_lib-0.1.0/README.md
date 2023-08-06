# Data Transformation Library

A Python library for common data transformations used in machine learning models.

## Installation

You can install the library using `pip`:

## Functions

### Transpose

The `transpose2d` function transposes a 2-dimensional matrix. It takes a 2-dimensional list as input and returns the transposed matrix.

### Time Series Windowing

The `window1d` function creates sliding windows of a specified size from a 1-dimensional array. It takes an input array, window size, shift value, and stride value as arguments and returns a list of sliding windows.

### Cross-Correlation

The `convolution2d` function performs cross-correlation between a 2-dimensional input matrix and a kernel. It takes a numpy array for the input matrix, kernel, and an optional stride value. It returns the result of the cross-correlation operation.