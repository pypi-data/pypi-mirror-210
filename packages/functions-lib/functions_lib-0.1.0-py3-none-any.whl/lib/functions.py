import numpy as np
from typing import List, Union, Optional
from dataclasses import dataclass

@dataclass
class TransposeOutput:
    transposed_matrix: List[List[float]]

@dataclass
class WindowOutput:
    windows: List[Union[List[float], np.ndarray]]

@dataclass
class ConvolutionOutput:
    result: np.ndarray

def transpose2d(input_matrix: List[List[float]]) -> TransposeOutput:
    """
    Transposes a 2-dimensional matrix.

    Args:
        input_matrix (List[List[float]]): The input matrix to be transposed.

    Returns:
        TransposeOutput: An instance of TransposeOutput containing the transposed matrix.

    Raises:
        Exception: If an error occurs during matrix transpose.
    """
    try:
        transposed_matrix = [[input_matrix[j][i] for j in range(len(input_matrix))] for i in range(len(input_matrix[0]))]
        # print("Matrix transposed successfully!")
        return TransposeOutput(transposed_matrix)
    except Exception as e:
        print("Error occurred during matrix transpose:", str(e))
        return None

def window1d(input_array: Union[List[float], np.ndarray], size: int, shift: int = 1, stride: int = 1) -> WindowOutput:
    """
    Creates sliding windows of a specified size from a 1-dimensional array.

    Args:
        input_array (Union[List[float], np.ndarray]): The input array.
        size (int): The size of the sliding window.
        shift (int, optional): The number of elements to shift the window by. Defaults to 1.
        stride (int, optional): The stride value for subsampling within the window. Defaults to 1.

    Returns:
        WindowOutput: An instance of WindowOutput containing the list of sliding windows.

    Raises:
        Exception: If an error occurs during time series windowing.
    """
    try:
        windows = []
        for i in range(0, len(input_array) - size + 1, shift):
            window = np.array(input_array[i:i+size])
            if stride > 1:
                window = window[::stride]
            windows.append(window)

        print("Time series windowing completed successfully!")
        return WindowOutput(windows=windows)
    except Exception as e:
        print("Error occurred during time series windowing:", str(e))
        return None

def convolution2d(input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1) -> Optional[ConvolutionOutput]:
    """
    Performs 2D convolution using a kernel on an input matrix.

    Args:
        input_matrix (np.ndarray): The input matrix.
        kernel (np.ndarray): The convolution kernel.
        stride (int, optional): The stride value for the convolution. Defaults to 1.

    Returns:
        ConvolutionOutput: An instance of ConvolutionOutput containing the result of the convolution.

    Raises:
        ValueError: If the input matrix dimensions are smaller than the kernel dimensions.
        Exception: If an error occurs during the convolution.
    """
    try:
        input_height, input_width = input_matrix.shape
        kernel_height, kernel_width = kernel.shape

        if input_height < kernel_height or input_width < kernel_width:
            raise ValueError("Input matrix dimensions should be greater than or equal to kernel dimensions.")

        output_height = (input_height - kernel_height) // stride + 1
        output_width = (input_width - kernel_width) // stride + 1

        output = np.zeros((output_height, output_width))

        for i in range(output_height):
            for j in range(output_width):
                patch = input_matrix[i*stride:i*stride+kernel_height, j*stride:j*stride+kernel_width]
                output[i, j] = np.sum(patch * kernel)

        print("Convolution completed successfully!")
        return ConvolutionOutput(result=output)
    except ValueError as ve:
        print("ValueError occurred during convolution:", str(ve))
        return None
    except Exception as e:
        print("Error occurred during convolution:", str(e))
        return None



