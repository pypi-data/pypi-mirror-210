import numpy as np
from BNumMet.Interpolation import polinomial

global exceptions
exceptions = [ValueError("The function has no zeros in the given interval")]


def bisect(f, interval, stop_iters=100, iters=False, *args):
    """
    Finds a zeros over the given interval using the Bisection method and tolerance ~ machine precision

    params:
        f: function to find the zeros
        interval: interval where the zeros are searched
        *args: arguments of the function f

    returns:
        x: zeros of the function f

    raises:
        ValueError: if the function has no zeros in the given interval

    """

    x0, x1 = interval
    # Evaluate the function at the two points of the interval
    f0 = f(x0, *args)
    f1 = f(x1, *args)

    # If the function has the same sign at the two points, raise an error as there's no zero between them
    if f0 * f1 > 0:
        raise exceptions[0]

    # Initialize x to the right endpoint of the interval
    x = x1
    # Initialize the iteration count to 0
    iterations = 0
    # Repeat the following loop until the function value at x is zero or the iteration count exceeds the maximum
    while f1 and iterations < stop_iters:
        # Increment the iteration count
        iterations += 1
        # Update x to be the midpoint of the interval
        x = 0.5 * (x0 + x1)
        # Evaluate the function at the new x
        faux = f(x, *args)
        # If the function has different signs at x and x1, set x0 to x
        if faux * f1 < 0:
            x0 = x
        # If the function has the same sign at x and x1, set x1 to x and update f1
        else:
            x1 = x
            f1 = faux
    # If the iters argument is set to True, return the zero of the function and the number of iterations taken
    if iters:
        return x, iterations
    # If the iters argument is set to False (default), return just the zero of the function
    return x


def secant(fun, interval, stop_iters=100, iters=False, *args):
    """
    Finds a zeros over the given interval using the secant method

    params:
        fun: function to find the zeros
        interval: interval where the zeros are searched
        *args: arguments of the function fun
        stop_iters: maximum number of iterations (default 100)
        iters: a flag to return the number of iterations performed (default False)

    returns:
        x: zeros of the function fun

    raises:
        ValueError: if the function has no zeros in the given interval

    """
    # Set initial values for x0, x1
    x0, x1 = interval
    # Evaluate the function at x0 and x1
    f0 = fun(x0, *args)
    f1 = fun(x1, *args)

    # Check if the product of f0 and f1 is greater than 0
    # If yes, raise a ValueError, as there is no zero in the interval
    if f0 * f1 > 0:
        raise ValueError("The function has no zeros in the given interval")

    # Initialize the number of iterations
    iterations = 0
    # Use the secant method to find the zero
    while abs(x1 - x0) > np.finfo(float).eps and iterations < stop_iters:
        # Increase the iteration count
        iterations += 1
        # Update the values of x2, x0, and x1
        x2 = x0
        x0 = x1
        x1 = x1 + (x1 - x2) / (fun(x2, *args) / fun(x1, *args) - 1)

    # Check if the flag `iters` is set to True
    if iters:
        # Return the zero and the number of iterations
        return x1, iterations
    # Return the zero
    return x1


def newton(fun, derivative, start_point, stop_iters=100, iters=False, *args):
    """
    Finds a zeros over the given interval using the Newton-Raphson method

    params:
        f: function to find the zeros
        interval: interval where the zeros are searched
        *args: arguments of the function f

    returns:
        x: zeros of the function f

    raises:
        ValueError: if the function has no zeros in the given interval

    """
    # initializing previousX with a value not equal to startPoint
    # and xn with the startPoint to allow for iteration
    previous_x = start_point - 1
    xn = start_point

    # evaluating the function at xn
    fn = fun(xn, *args)

    # checking if the derivative of the function at xn is zero
    # and raising an error if it is
    if derivative(xn, *args) == 0:
        raise ValueError("The derivative of the function is zero")

    # initializing iteration count to zero
    iterations = 0

    # checking if the function at xn is not equal to zero
    # and that xn is not equal to previousX and the derivative
    # of the function at xn is not equal to zero and that
    # the number of iterations is less than the stopping criteria
    while (
        fn != 0
        and not np.isclose(xn - previous_x, 0)
        and derivative(xn, *args) != 0
        and iterations < stop_iters
    ):
        # incrementing iteration count by one
        iterations += 1

        # updating previousX with the current value of xn
        previous_x = xn
        # updating xn with the next iteration value
        # computed using the Newton-Raphson method
        xn = xn - fn / derivative(xn, *args)
        # evaluating the function at xn
        fn = fun(xn, *args)

    # if the iters flag is set, return xn and the number of iterations
    # otherwise return only xn
    if iters:
        return xn, iterations
    return xn


def IQI(f, x_values, stop_iters=100, iters=False, *args):
    """
    Finds a zeros over the given interval using the Inverse Quadratic Interpolation method

    params:
        f: function to find the zeros
        xVals : [x0,x1,x2]
        *args: arguments of the function f

    returns:
        x: zeros of the function f

    raises:
        ValueError: if the function has no zeros in the given interval

    """
    # Unpacking the initial values for x0, x1 and x2
    x0, x1, x2 = x_values
    # Initializing the iteration counter to 0
    iterations = 0
    # The main loop, where the inverse quadratic interpolation is performed
    # This loop continues until either the relative difference between x1 and x0 is less than the machine precision
    # or the number of iterations has reached the maximum allowed iterations
    while abs(x1 - x0) > np.finfo(float).eps and iterations < stop_iters:
        # Increase the iteration counter
        iterations += 1
        # Evaluate the function at x0, x1, and x2
        f0, f1, f2 = f(x0, *args), f(x1, *args), f(x2, *args)
        # Perform the inverse quadratic interpolation
        aux1 = (x0 * f1 * f2) / ((f0 - f1) * (f0 - f2))
        aux2 = (x1 * f0 * f2) / ((f1 - f0) * (f1 - f2))
        aux3 = (x2 * f1 * f0) / ((f2 - f0) * (f2 - f1))
        new = aux1 + aux2 + aux3
        # Shift x0, x1, x2 to the right by 1 position
        x0, x1, x2 = new, x0, x1

    # If the argument iters is set to True, return both the result and the number of iterations
    if iters:
        return x0, iterations
    # Otherwise, return only the result
    return x0


def zBrentDekker(
    f, interval, tol=10 ** (-20), stop_iters=100, iters=False, steps=False, *args
):
    """
    Finds a zeros over the given interval using a combination of Bisection and secant method

    params:
        f: function to find the zeros
        interval: interval where the zeros are searched
        *args: arguments of the function f

    returns:
        x: zeros of the function f

    raises:
        ValueError: if the function has no zeros in the given interval

    """
    # Split the interval into a and b
    a, b = interval
    # Evaluate the function at a and b
    fa = f(a, *args)
    fb = f(b, *args)

    # Check if there are no zeros in the interval
    if fa * fb > 0:  # No zeros guaranteed in the interval
        raise exceptions[0]

    # Initialize the variables for the internal section
    c, fc, d, e = a, fa, b - a, b - a

    # Check if fc is smaller than fb, if so swap the values
    if abs(fc) < abs(fb):
        a, b, c, fa, fb, fc = b, c, b, fb, fc, fb

    # Calculate the tolerance level
    tolerance = 2 * np.finfo(float).eps * abs(b) + tol
    m = 0.5 * (c - b)

    # Initialize iteration and procedure stack
    iterations = 0
    procedure_stack = []

    # Repeat until the tolerance level is met or max iterations is reached
    while abs(m) > tolerance and fb and iterations < stop_iters:
        # Calculate next step
        # =============================================================================================================
        # Check if bisection is forced
        if abs(e) < tolerance or abs(fa) <= abs(fb):
            d = m
            e = m
            procedure_stack.append("Bisection")
        else:
            # Calculate the ratio of fb and fa
            s = fb / fa
            if a == c:
                # Use linear interpolation
                p = 2 * m * s
                q = 1 - s
            else:
                # Use inverse quadratic interpolation
                q = fa / fc
                r = fb / fc
                p = s * (2 * m * q * (q - r) - (b - a) * (r - 1))
                q = (q - 1) * (r - 1) * (s - 1)

            # Correct the sign of p and q
            if p > 0:
                q = -q
            else:
                p = -p

            s = e
            e = d

            # Validate the interpolation
            if 2 * p < 3 * m * q - abs(tolerance * q) and p < abs(0.5 * s * q):
                # The interpolation is valid
                d = p / q
                procedure_stack.append("IQI" if a != c else "Secant")
            else:
                # The interpolation is not valid, we use bisection
                d = m
                e = m
                procedure_stack.append("Bisection")
        a = b
        fa = fb

        b += d if abs(d) > tolerance else np.sign(m) * tolerance
        fb = f(b, *args)
        # =============================================================================================================

        # Update interval
        # =============================================================================================================
        # Correct points accordingly
        if np.sign(fb) == np.sign(fc) != 0:
            # Section: int
            c, fc, d, e = a, fa, b - a, b - a
        # Section: ext
        elif abs(fc) < abs(fb):
            a, b, c, fa, fb, fc = b, c, b, fb, fc, fb

        # Update tolerance and m for the next iteration
        tolerance = 2 * np.finfo(float).eps * abs(b) + tol
        m = 0.5 * (c - b)

        iterations += 1
        # print(b,e)
    zero = b
    if steps and iters:
        return zero, iterations, procedure_stack
    if iters:
        return zero, iterations
    if steps:
        return zero, procedure_stack
    return zero
