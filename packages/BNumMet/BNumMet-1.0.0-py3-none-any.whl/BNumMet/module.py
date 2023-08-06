import numpy as np


def pretty_print_matrix(matrix):
    """
    Prints a matrix in a pretty format

    Parameters
    ----------
    matrix : list
        The matrix to print

    Returns
    -------
    res : str
        The string representation of the matrix in a pretty format for LaTeX
    """
    # Initialize the string to represent the matrix
    res = " \\begin{pmatrix}\n"

    # Loop through each row in the matrix
    for row in matrix:
        # Join the elements in each row with " & " and add a line break at the end
        res += " & ".join([str(x) for x in row]) + "\\\\\n"

    # Close the matrix representation
    res += "\end{pmatrix}"

    # Return the final string
    return res


def sort_interpolation_values(x, y):
    """
    Sorts the interpolation values by the x coordinates

    Parameters
    ----------
    x : list
        The x coordinates of the interpolation values
    y : list
        The y coordinates of the interpolation values

    Returns
    -------
    x : list
        The sorted x coordinates of the interpolation values
    y : list
        The sorted y coordinates of the interpolation values
    """
    x = np.array(x)  # Convert the x coordinates to a numpy array
    y = np.array(y)  # Convert the y coordinates to a numpy array
    ind = np.argsort(x)  # Get the indices of the sorted array
    x = x[ind]  # Sort the x coordinates
    y = y[ind]  # Sort the y coordinates

    return x, y


def pretty_plua(P, L, U, A):
    res = f""" 
    \\begin{{array}}{{lll}}
        P = {pretty_print_matrix(P)} & L = {pretty_print_matrix(L)} & U = {pretty_print_matrix(U)} 
        \\\\
        &&
        \\\\
        P\cdot A = {pretty_print_matrix(P@A)} &  L\cdot U = {pretty_print_matrix(L@U)}
    \\end{{array}}
    """
    return res
