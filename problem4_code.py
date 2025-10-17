def find_gcd(a: int, b: int):
    """
    Implements the Euclidean Algorithm to find the greatest common divisor of two integers.
    
    Args:
        a: A positive integer
        b: A positive integer
    
    Returns:
        A tuple containing:
        - The GCD as the first item
        - The number of division operations needed as the second item
    
    Raises:
        Exception: If a or b are not positive integers
    
    Examples:
        find_gcd(124, 12) returns (4, 2)
        find_gcd(476, 630) returns (14, 3)
    """
    
    # Validate that both inputs are integers
    if not isinstance(a, int) or not isinstance(b, int):
        raise Exception("Both a and b must be integers")
    
    # Validate that both inputs are positive
    if a <= 0 or b <= 0:
        raise Exception("Both a and b must be positive integers")
    
    # Initialize division operation counter
    division_count = 0
    
    # Step 1: If a < b, exchange a and b
    if a < b:
        a, b = b, a
    
    # Step 2-3: Apply the Euclidean algorithm
    while b != 0:
        # Divide a by b and get the remainder
        remainder = a % b
        division_count += 1
        
        # Replace a with b and b with remainder
        a = b
        b = remainder
    
    # When b becomes 0, a is the GCD
    return (a, division_count)