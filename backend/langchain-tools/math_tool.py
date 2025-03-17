from langchain_core.tools import tool
import math
import statistics
from typing import List, Union, Optional


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    return a * b


@tool
def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the result."""
    return a - b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b and return the result. Raises an error if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@tool
def power(base: float, exponent: float) -> float:
    """Calculate base raised to the power of exponent."""
    return math.pow(base, exponent)


@tool
def square_root(number: float) -> float:
    """Calculate the square root of a number. Raises an error if number is negative."""
    if number < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(number)


@tool
def calculate_mean(numbers: List[float]) -> float:
    """Calculate the arithmetic mean (average) of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate mean of an empty list")
    return statistics.mean(numbers)


@tool
def calculate_median(numbers: List[float]) -> float:
    """Calculate the median (middle value) of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate median of an empty list")
    return statistics.median(numbers)


@tool
def calculate_standard_deviation(numbers: List[float]) -> float:
    """Calculate the standard deviation of a list of numbers."""
    if len(numbers) < 2:
        raise ValueError("Need at least two values to calculate standard deviation")
    return statistics.stdev(numbers)


@tool
def calculate_percentage(value: float, total: float) -> float:
    """Calculate what percentage value is of total."""
    if total == 0:
        raise ValueError("Total cannot be zero")
    return (value / total) * 100


@tool
def round_number(number: float, decimal_places: Optional[int] = None) -> float:
    """Round a number to the specified number of decimal places."""
    if decimal_places is None:
        return round(number)
    return round(number, decimal_places)


@tool
def calculate_factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer n (n!)."""
    if n < 0:
        raise ValueError("Cannot calculate factorial of a negative number")
    return math.factorial(n)


@tool
def calculate_logarithm(number: float, base: Optional[float] = 10) -> float:
    """Calculate the logarithm of a number with the specified base (default is base 10)."""
    if number <= 0:
        raise ValueError("Number must be positive for logarithm calculation")
    if base <= 0 or base == 1:
        raise ValueError("Base must be positive and not equal to 1")
    
    if base == 10:
        return math.log10(number)
    elif base == math.e:
        return math.log(number)
    else:
        return math.log(number, base)


@tool
def solve_quadratic_equation(a: float, b: float, c: float) -> List[float]:
    """
    Solve a quadratic equation of the form ax² + bx + c = 0.
    Returns a list of solutions (can be 0, 1, or 2 solutions).
    """
    if a == 0:
        if b == 0:
            raise ValueError("Not a valid quadratic equation (a and b are both zero)")
        return [-c / b]  # Linear equation
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        raise ValueError("No real solutions (discriminant is negative)")
    elif discriminant == 0:
        return [-b / (2*a)]  # One solution
    else:
        sqrt_discriminant = math.sqrt(discriminant)
        return [(-b + sqrt_discriminant) / (2*a), (-b - sqrt_discriminant) / (2*a)]


