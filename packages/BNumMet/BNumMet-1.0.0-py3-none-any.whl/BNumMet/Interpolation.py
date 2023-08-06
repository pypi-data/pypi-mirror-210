import numpy as np
from BNumMet.LinearSystems import lu_solve


def polinomial(x, y, u):
    """
    Computes the polynomial interpolation of a set of points (x,y) at the points u

    params:
        x: list of x coordinates  # list of x coordinates of the input data points
        y: list of y coordinates  # list of y coordinates of the input data points
        u: list of points where the interpolation is computed  # list of points where the interpolation is to be computed

    returns:
        v: list of values of the interpolation at the points u  # list of interpolated values at the specified points u
    """
    n = len(x)  # number of input data points
    v = np.zeros(
        len(u)
    )  # Create a vector of zeros of the same size as u, to store the result
    for i in range(n):
        w = np.ones(len(u))  # initializing the weight vector with ones
        for j in range(n):
            if j != i:  # exclude current data point from calculation of weights
                w *= (u - x[j]) / (
                    x[i] - x[j]
                )  # calculate weight for current data point
        v += (
            w * y[i]
        )  # accumulate weighted y values to get the final interpolated value

    return v  # return the final interpolated values


def piecewise_linear(x, y, u, sorted=False):
    """
    Computes the piecewise lineal interpolation of a set of points (x,y) at the points u, (x,y) ACCORDING TO THE ALGORITHM IN THE BOOK

    params:
        x: list of x coordinates  # list of x coordinates of the input data points
        y: list of y coordinates  # list of y coordinates of the input data points
        u: list of points where the interpolation is computed  # list of points where the interpolation is to be computed
        sorted (optional): if the points are sorted or not (default: False)  # boolean flag indicating if the input data points are sorted or not

    returns:
        v: list of values of the interpolation at the points u  # list of interpolated values at the specified points u
    """
    if not sorted:  # if the input data points are not sorted
        # Sort the points
        x = np.array(x)  # convert x to numpy array
        y = np.array(y)  # convert y to numpy array
        ind = np.argsort(x)  # Get the indices of the sorted array
        x = x[ind]  # Sort the x coordinates
        y = y[ind]  # Sort the y coordinates

    delta = np.diff(y) / np.diff(
        x
    )  # Compute the slopes of the lines -- here we are using the fact that x is sorted
    n = len(x)  # number of input data points

    k = np.zeros(np.size(u), dtype=int)  # initialize array to store indices
    for j in np.arange(1, n - 1):
        k[
            x[j] <= u
        ] = j  # find the indices of the data points just smaller than the corresponding u values

    s = u - x[k]  # calculate the difference between u and corresponding x values
    v = (
        y[k] + s * delta[k]
    )  # calculate the interpolated y values based on the slope of the line

    return v  # return the final interpolated values


def pchip(x, y, u, sorted=False):
    """
    Piecewise Cubic Hermite Interpolation Polynomial (P.C.H.I.P.) [Based on an old Fortran program by Fritsch and Carlson]

        params:
            x: list of x coordinates
            y: list of y coordinates
            u: list of points where the interpolation is computed
            sorted (optional): if the points are sorted or not (default: False)

        returns:
            v: list of values of the interpolation at the points u
    """

    def pchip_end(h1, h2, delta1, delta2):
        """
        Computes the slopes at the end points of the interval

        params:
            x: list of x coordinates # x-coordinates of the data points
            y: list of y coordinates # y-coordinates of the data points
            u: list of points where the interpolation is computed # Points where the interpolation is to be computed
            sorted (optional): if the points are sorted or not (default: False) # Parameter to specify if the points are already sorted

        returns:
            v: list of values of the interpolation at the points u # List of values of the P.C.H.I.P. at the points in 'u'
        """
        # Noncenter, shape-preserving, three-point formula.
        d = ((2 * h1 + h2) * delta1 - h1 * delta2) / (h1 + h2)
        # If slopes of the secant lines are of different sign or If the slopes are not of the same magnitude, use 0.
        if (
            np.sign(delta1) != np.sign(delta2)
            or np.abs(d) > np.abs(3 * delta1)
            or np.abs(d) > np.abs(3 * delta2)
        ):
            d = 0

        return d

    def pchip_slopes(h, delta):
        """
        Slopes for shape-preserving Hermite cubic, computes the slopes
            - Interior Points
                * d(k) = 0 <- delta(k-1) && delta(k) different signs or both are 0
                * d(k) = Weighted Harmonic Mean <- Same sign delta(k-1) && delta (k)
            - EndPoints
                Call pchip end :)

        params:
            h: list of distances between points
            delta: list of slopes between points

        returns:
            d: list of slopes for the Hermite cubic
        """
        d = np.zeros(len(h))  # Initialize an array of zeros to store the slopes

        k = np.where(np.sign(delta[0:-1]) * np.sign(delta[1:]) > 0)[
            0
        ]  # Find the indices of the points where the slopes are of the same sign. 'k' will be an array of indices.
        k = k + 1  # Add 1 to the indices to get the indices of the slopes

        w1 = 2 * h[k] + h[k - 1]
        w2 = h[k] + 2 * h[k - 1]
        d[k] = (w1 + w2) / (
            w1 / delta[k - 1] + w2 / delta[k]
        )  # Compute the slopes of the lines for the interior points, where the slopes are of the same sign

        # end points
        d[0] = pchip_end(
            h[0], h[1], delta[0], delta[1]
        )  # Compute the slope of the first endpoint using the 'pchip_end' function

        d = np.append(
            d, pchip_end(h[-2], h[-3], delta[-2], delta[-3])
        )  # Compute the slope of the last endpoint using the 'pchip_end' function and append it to 'd'

        return d  # Return the list of slopes

    # Sort the points
    x = np.array(x)  # Convert the x coordinate input to a numpy array
    y = np.array(y)  # Convert the y coordinate input to a numpy array
    if not sorted:  # If the points are not already sorted
        ind = np.argsort(x)  # Get the indices of the sorted array
        x = x[ind]  # Sort the x coordinates
        y = y[ind]  # Sort the y coordinates

    # First derivative
    h = np.diff(x)  # Compute the distances between the points in x
    delta = np.diff(y) / h  # Compute the slopes between the points

    d = pchip_slopes(
        h, delta
    )  # Compute the slopes for the Hermite cubic using the pchip_slopes function

    n = len(x)
    c = (3 * delta - 2 * d[:-1] - d[1:]) / (
        h
    )  # Compute the coefficients of the cubic polynomials
    b = (d[:-1] - 2 * delta + d[1:]) / (
        h**2
    )  # Compute the coefficients of the cubic polynomials

    k = np.zeros(np.size(u), dtype=int)  # Initialize an array of indices
    for j in np.arange(1, n - 1):  # Loop through the indices
        k[x[j] <= u] = j  # Update the indices where x[j] is less than or equal to u

    s = u - x[k]  # Compute the value of s for each index
    v = y[k] + s * (
        d[k] + s * (c[k] + s * b[k])
    )  # Compute the values of the Hermite cubic

    return v  # Return the computed values


def splines(x, y, u, sorted=False):
    """
    Finds the piecewise cubic interpolatory spline S(x), with S(x(j)) = y(j), and returns v(k) = S(u(k)).

    params:
        x: list of x coordinates - list of x values to be used as input to the spline
        y: list of y coordinates - list of y values to be used as input to the spline
        u: list of points where the interpolation is computed - the list of x-coordinates where the spline should be evaluated
        sorted (optional): if the points are sorted or not (default: False) - flag to indicate whether the input points are sorted or not

    returns:
        v: list of values of the interpolation at the points u - the y-values of the spline evaluated at the x-coordinates in u
    """

    def splineslopes(h, delta):
        """
        Computes the slopes of the splines Uses not-a-knot end conditions.

        params:
            h: list of distances between points
            delta: list of slopes between points

        returns:
            d: list of slopes for the splines
        """
        # Initialize arrays for the coefficients of the tridiagonal matrix
        a = np.zeros(len(h)).astype(float)
        b = np.zeros(len(h)).astype(float)
        c = np.zeros(len(h)).astype(float)
        r = np.zeros(len(h)).astype(float)

        # Set values for the first and second sub-diagonal of the matrix
        a[:-1] = h[1:]  # Set values for all but the last entry of `a`
        a[-1] = h[-2] + h[-1]  # Set value for the last entry of `a`
        b[0] = h[1]  # Set the first value of `b`
        b[1:] = 2 * (h[1:] + h[:-1])  # Set values for all but the first entry of `b`
        b = np.append(b, h[-2])  # Append the value of `h[-2]` to the end of `b`
        c[0] = h[0] + h[1]  # Set the first value of `c`
        c[1:] = h[:-1]  # Set values for all but the first entry of `c`

        # Right-hand side

        # Calculate the first value of the right-hand side
        r[0] = ((h[0] + 2 * c[0]) * h[1] * delta[0] + h[0] ** 2 * delta[1]) / c[0]
        # Calculate values for all but the first entry of the right-hand side
        r[1:] = 3 * (h[1:] * delta[:-1] + h[:-1] * delta[1:])
        # Append a calculated value to the end of the right-hand side
        r = np.append(
            r,
            (h[-1] ** 2 * delta[-2] + (2 * a[-1] + h[-1]) * h[-2] * delta[-1]) / a[-1],
        )

        # Solve the system of equations defined by the tridiagonal matrix and the right-hand side
        res = lu_solve(np.diag(a, -1) + np.diag(b) + np.diag(c, 1), r)

        # Return the solution with type `float`
        return res.astype(float)

    x = np.array(
        x
    )  # Convert the input x data into a numpy array, if it is not already one
    y = np.array(
        y
    )  # Convert the input y data into a numpy array, if it is not already one

    if not sorted:  # If the input points are not sorted in ascending order of x values
        # Sort the points
        ind = np.argsort(x)  # Get the indices of the sorted array after sorting x
        x = x[ind]  # Sort the x coordinates
        y = y[ind]  # Sort the y coordinates

    # First derivative
    h = np.diff(x)  # Calculate the differences between consecutive x values
    delta = (
        np.diff(y) / h
    )  # Calculate the differences between consecutive y values and divide by the differences in x to obtain the first derivative at each point

    d = splineslopes(
        h, delta
    )  # Calculate the slopes of the cubic spline using the helper function `splineslopes` and the calculated differences in x and y

    n = len(x)  # Get the number of points
    c = (3 * delta - 2 * d[:-1] - d[1:]) / (
        h
    )  # Calculate the coefficient c for the cubic spline
    b = (d[:-1] - 2 * delta + d[1:]) / (
        h**2
    )  # Calculate the coefficient b for the cubic spline

    k = np.zeros(
        np.size(u), dtype=int
    )  # Create an array of zeros with the same number of elements as the input u, with data type integer
    for j in np.arange(1, n - 1):  # Loop through all values from 1 to n-1
        k[
            x[j] <= u
        ] = j  # If the j-th value in x is less than or equal to u, set the corresponding value in k to j

    s = (
        u - x[k]
    )  # Calculate the difference between u and the value in x at the corresponding index in k
    v = y[k] + s * (
        d[k] + s * (c[k] + s * b[k])
    )  # Calculate the value of the cubic spline at each point in u using the calculated coefficients and the differences in x and y

    return v  # Return the calculated value of the cubic spline at each point in u
