import math
import simpleeval
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import ast
import operator

def format_num(val):
    """
    Formats a number cleanly.
    - If it's a complex number, it formats as a + bi or a - bi.
    - If it's an integer or a float representing an integer, returns an int.
    - Rounds floats to 10 decimal places to handle floating-point precision issues.
    """
    if isinstance(val, complex):
        real = format_num(val.real)
        imag = format_num(val.imag)
        if imag == 0:
            return real
        if real == 0:
            return f"{imag}i"
        sign = "+" if imag > 0 else "-"
        abs_imag = abs(imag)
        if abs_imag == 1:
            return f"{real} {sign} i"
        return f"{real} {sign} {abs_imag}i"
    
    if isinstance(val, (float, int)):
        if isinstance(val, float):
            if val.is_integer():
                return int(val)
            # Handle float precision roundoffs (e.g. 0.1 + 0.2)
            rounded = round(val, 10)
            if rounded.is_integer():
                return int(rounded)
            return rounded
        return val
    return val

class MathEvaluator:
    """
    A safe expression evaluator that extends simpleeval with rich math features
    and stateful calculation (ans) memory per channel.
    """
    def __init__(self):
        self.channel_memories = {}

    def eval_expression(self, expression: str, channel_id: int):
        # We limit the length to prevent resource abuse/overloads
        if len(expression) > 100:
            raise ValueError("Expression is too long (maximum 100 characters)!")

        # Set up custom names (constants)
        names = simpleeval.DEFAULT_NAMES.copy()
        names.update({
            'pi': math.pi,
            'π': math.pi,
            'e': math.e,
            'tau': math.tau,
            'τ': math.tau,
            'inf': math.inf,
            'nan': math.nan,
            'ans': self.channel_memories.get(channel_id, {}).get('ans', 0)
        })

        # Helper wrappers for functions with variable or safe arguments
        def safe_log(x, base=None):
            if base is None:
                return math.log(x)
            return math.log(x, base)

        def safe_round(x, ndigits=None):
            if ndigits is None:
                return round(x)
            return round(x, int(ndigits))

        # Set up custom functions
        functions = simpleeval.DEFAULT_FUNCTIONS.copy()
        functions.update({
            # Trigonometry
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'radians': math.radians,
            'rad': math.radians,
            'degrees': math.degrees,
            'deg': math.degrees,
            
            # Roots and Logs
            'sqrt': math.sqrt,
            'cbrt': lambda x: x ** (1/3),
            'abs': abs,
            'log': safe_log,
            'log10': math.log10,
            'log2': math.log2,
            'ln': math.log,
            'exp': math.exp,
            
            # Utilities
            'ceil': math.ceil,
            'floor': math.floor,
            'round': safe_round,
            'factorial': math.factorial,
            'fact': math.factorial,
            'gcd': math.gcd,
            'lcm': math.lcm if hasattr(math, 'lcm') else lambda a, b: abs(a*b) // math.gcd(a, b),
        })

        # Evaluate safely
        s = simpleeval.SimpleEval(names=names, functions=functions)
        result = s.eval(expression)
        
        # Save result to channel memory if it's a valid number
        if isinstance(result, (int, float)) and not math.isnan(result) and not math.isinf(result):
            if channel_id not in self.channel_memories:
                self.channel_memories[channel_id] = {}
            self.channel_memories[channel_id]['ans'] = result
            
        return result

def analyze_stats(numbers):
    """
    Computes a complete set of statistical descriptors for a list of numbers.
    """
    if not numbers:
        raise ValueError("List of numbers cannot be empty.")
    
    count = len(numbers)
    total = sum(numbers)
    mean = total / count
    
    # Median
    sorted_nums = sorted(numbers)
    if count % 2 == 1:
        median = sorted_nums[count // 2]
    else:
        median = (sorted_nums[count // 2 - 1] + sorted_nums[count // 2]) / 2
        
    # Mode
    from collections import Counter
    counts = Counter(numbers)
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count]
    if len(modes) == count:
        mode_str = "No unique mode"
    else:
        mode_str = ", ".join(str(format_num(m)) for m in modes)
        
    # Variance and Standard Deviation (sample variance for count > 1)
    if count > 1:
        variance = sum((x - mean) ** 2 for x in numbers) / (count - 1)
    else:
        variance = 0.0
    stddev = math.sqrt(variance)
    
    return {
        "count": count,
        "sum": total,
        "mean": mean,
        "median": median,
        "mode": mode_str,
        "variance": variance,
        "stddev": stddev,
        "min": min(numbers),
        "max": max(numbers)
    }

def factor_prime(n):
    """
    Checks primality, generates prime factorization, and list of divisors.
    """
    if n < 1:
        raise ValueError("Number must be greater than 0.")
    if n > 1000000000:
        raise ValueError("Number is too large (maximum 1,000,000,000)!")
    
    if n == 1:
        return {"is_prime": False, "factors": {}, "divisors": [1]}
        
    temp = n
    factors = {}
    
    # Extract factor 2
    while temp % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        temp //= 2
        
    # Extract odd factors
    i = 3
    while i * i <= temp:
        while temp % i == 0:
            factors[i] = factors.get(i, 0) + 1
            temp //= i
        i += 2
        
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
        
    is_prime = (len(factors) == 1 and list(factors.values())[0] == 1)
    
    # Calculate all divisors
    divisors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divisors.append(i)
            if i * i != n:
                divisors.append(n // i)
    divisors.sort()
    
    return {
        "is_prime": is_prime,
        "factors": factors,
        "divisors": divisors
    }

def solve_equation(a, b, c=None):
    """
    Solves linear (ax + b = 0) or quadratic (ax^2 + bx + c = 0) equations.
    """
    if c is None:
        # Linear: ax + b = 0
        if a == 0:
            if b == 0:
                return "Infinite solutions"
            else:
                return "No solution"
        return [-b / a]
    else:
        # Quadratic: ax^2 + bx + c = 0
        if a == 0:
            # Fallback to linear: bx + c = 0
            return solve_equation(b, c)
        
        discriminant = b**2 - 4*a*c
        if discriminant > 0:
            r1 = (-b + math.sqrt(discriminant)) / (2 * a)
            r2 = (-b - math.sqrt(discriminant)) / (2 * a)
            return [r1, r2]
        elif discriminant == 0:
            return [-b / (2 * a)]
        else:
            real_part = -b / (2 * a)
            imag_part = math.sqrt(-discriminant) / (2 * a)
            r1 = complex(real_part, imag_part)
            r2 = complex(real_part, -imag_part)
            return [r1, r2]

def convert_units(value, from_unit, to_unit):
    """
    High-accuracy unit converter across temperature, length, weight, and data.
    """
    from_u = from_unit.strip().lower()
    to_u = to_unit.strip().lower()
    
    # Temperature
    temp_map = {'c', 'f', 'k', 'celsius', 'fahrenheit', 'kelvin'}
    if from_u in temp_map and to_u in temp_map:
        if from_u in ('c', 'celsius'):
            c = value
        elif from_u in ('f', 'fahrenheit'):
            c = (value - 32) * 5 / 9
        else:
            c = value - 273.15
        
        if to_u in ('c', 'celsius'):
            return c
        elif to_u in ('f', 'fahrenheit'):
            return c * 9 / 5 + 32
        else:
            return c + 273.15
            
    # Length (base: meter)
    length_rates = {
        'm': 1.0, 'meter': 1.0, 'meters': 1.0,
        'cm': 0.01, 'centimeter': 0.01, 'centimeters': 0.01,
        'mm': 0.001, 'millimeter': 0.001, 'millimeters': 0.001,
        'km': 1000.0, 'kilometer': 1000.0, 'kilometers': 1000.0,
        'in': 0.0254, 'inch': 0.0254, 'inches': 0.0254,
        'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
        'yd': 0.9144, 'yard': 0.9144, 'yards': 0.9144,
        'mi': 1609.344, 'mile': 1609.344, 'miles': 1609.344
    }
    
    # Weight/Mass (base: gram)
    weight_rates = {
        'g': 1.0, 'gram': 1.0, 'grams': 1.0,
        'mg': 0.001, 'milligram': 0.001, 'milligrams': 0.001,
        'kg': 1000.0, 'kilogram': 1000.0, 'kilograms': 1000.0,
        'lb': 453.59237, 'pound': 453.59237, 'pounds': 453.59237,
        'oz': 28.349523125, 'ounce': 28.349523125, 'ounces': 28.349523125
    }
    
    # Digital Data (base: Byte, using binary 1024)
    data_rates = {
        'b': 0.125, 'bit': 0.125, 'bits': 0.125,
        'byte': 1.0, 'bytes': 1.0, 'B': 1.0,
        'kb': 1024.0, 'kilobyte': 1024.0, 'kilobytes': 1024.0,
        'mb': 1024.0**2, 'megabyte': 1024.0**2, 'megabytes': 1024.0**2,
        'gb': 1024.0**3, 'gigabyte': 1024.0**3, 'gigabytes': 1024.0**3,
        'tb': 1024.0**4, 'terabyte': 1024.0**4, 'terabytes': 1024.0**4
    }
    
    def find_rate(unit, rates):
        if unit in rates:
            return rates[unit]
        unit_lower = unit.lower()
        for k, v in rates.items():
            if k.lower() == unit_lower:
                return v
        return None
        
    # Try Length
    from_rate = find_rate(from_unit, length_rates)
    to_rate = find_rate(to_unit, length_rates)
    if from_rate is not None and to_rate is not None:
        return value * from_rate / to_rate
        
    # Try Weight
    from_rate = find_rate(from_unit, weight_rates)
    to_rate = find_rate(to_unit, weight_rates)
    if from_rate is not None and to_rate is not None:
        return value * from_rate / to_rate
        
    # Try Data (checking exact match first to preserve 'b' vs 'B' distinction)
    from_rate_data = data_rates.get(from_unit) or find_rate(from_unit, data_rates)
    to_rate_data = data_rates.get(to_unit) or find_rate(to_unit, data_rates)
    if from_rate_data is not None and to_rate_data is not None:
        return value * from_rate_data / to_rate_data
        
    raise ValueError(f"Unsupported or incompatible units: '{from_unit}' to '{to_unit}'")

def generate_plot(expression: str, x_min: float = -10, x_max: float = 10) -> io.BytesIO:
    """
    Safely parses and renders a single-variable expression in terms of 'x'
    to a Discord-themed dark mode plot in a memory buffer.
    """
    if len(expression) > 100:
        raise ValueError("Expression is too long (maximum 100 characters)!")

    if x_min >= x_max:
        raise ValueError("Minimum x value must be less than maximum x value.")

    # 1. Evaluate coordinate values safely using vectorized NumPy
    # Generate 500 smooth sample points
    x_coords = np.linspace(x_min, x_max, 500)
    
    names = {
        'x': x_coords,
        'pi': np.pi,
        'π': np.pi,
        'e': np.e,
        'tau': 2 * np.pi,
        'τ': 2 * np.pi
    }

    # Vectorized NumPy functions mapped to safe names
    functions = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'asin': np.arcsin,
        'acos': np.arccos,
        'atan': np.arctan,
        'sinh': np.sinh,
        'cosh': np.cosh,
        'tanh': np.tanh,
        'radians': np.radians,
        'rad': np.radians,
        'degrees': np.degrees,
        'deg': np.degrees,
        'sqrt': np.sqrt,
        'cbrt': np.cbrt,
        'abs': np.abs,
        'log': lambda x, base=None: np.log(x) if base is None else np.log(x) / np.log(base),
        'log10': np.log10,
        'log2': np.log2,
        'ln': np.log,
        'exp': np.exp,
        'ceil': np.ceil,
        'floor': np.floor,
        'round': np.round,
    }

    # Safe evaluation
    try:
        # Override safe check operators that fail on NumPy vectorized evaluation
        operators = simpleeval.DEFAULT_OPERATORS.copy()
        operators.update({
            ast.Pow: operator.pow,
            ast.Add: operator.add,
            ast.Mult: operator.mul,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
        })
        s = simpleeval.SimpleEval(names=names, functions=functions, operators=operators)
        y_coords = s.eval(expression)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {str(e)}")

    # Ensure y_coords is a NumPy array
    if isinstance(y_coords, (int, float)):
        # Constant line
        y_coords = np.full_like(x_coords, y_coords)
    elif not isinstance(y_coords, np.ndarray):
        raise ValueError("Expression did not return a numeric sequence.")

    # 2. Render plot using custom Discord-themed Dark Mode styles
    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#313338')
    ax.set_facecolor('#313338')

    # Draw translucent grid lines
    ax.grid(True, color='#4e5058', linestyle='--', linewidth=0.6, alpha=0.4)

    # Plot the vibrant neon cyan line curve
    ax.plot(x_coords, y_coords, color='#00e5ff', linewidth=2.5, label=expression)

    # Spine styling
    for spine in ax.spines.values():
        spine.set_color('#4e5058')
        spine.set_linewidth(0.8)
        
    # Configure axes tick/label styles
    ax.tick_params(colors='#ffffff', labelsize=9)
    ax.xaxis.label.set_color('#ffffff')
    ax.yaxis.label.set_color('#ffffff')
    
    # Smart range clipping to ignore vertical asymptote spikes
    finite_mask = np.isfinite(y_coords)
    valid_y = y_coords[finite_mask]
    if len(valid_y) > 0:
        y_min_val, y_max_val = np.percentile(valid_y, [2, 98])
        margin = (y_max_val - y_min_val) * 0.1
        if margin == 0:
            margin = 1.0
        ax.set_ylim(y_min_val - margin, y_max_val + margin)
    else:
        ax.set_ylim(-10, 10)

    ax.set_xlim(x_min, x_max)

    # Set title styled cleanly in white
    ax.set_title(f"Plot of y = {expression}", color='#ffffff', fontsize=12, pad=12, fontweight='bold')
    
    # Save directly to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='#313338')
    buf.seek(0)
    
    plt.close(fig)
    
    return buf
