from unittest import TestCase
from BNumMet.module import pretty_print_matrix, sort_interpolation_values, pretty_plua
from BNumMet.LinearSystems import lu
import numpy as np


class test_module(TestCase):
    def test_PrettyPrint(self):
        matrix = [[1, 2], [3, 4]]
        stringRes = """ \\begin{pmatrix}1 & 2\\\\3 & 4\\\\\\end{pmatrix}"""

        self.assertTrue(pretty_print_matrix(matrix).replace("\n", "") == stringRes)

    def test_SortInterpolVals(self):
        x = [1, 3, 2]
        y = [4, 3, 2]
        xRes = [1, 2, 3]
        yRes = [4, 2, 3]
        x, y = sort_interpolation_values(x, y)

        self.assertTrue((x == xRes).all() and (y == yRes).all())

    def test_pretty_plua(self):
        matrix = [[1, 2], [3, 4]]

        p, l, u = lu(np.array(matrix))
        res = pretty_plua(p, l, u, matrix)
        # assert type of p, l, u, a is str
        self.assertTrue(type(res) == str)
