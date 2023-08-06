import sys
import os
from unittest import TestCase
import unittest
import numpy as np
from random import randint

from BNumMet.Visualizers.LeastSquaresVisualizer import LSPVisualizer as LSV


class Test_LSPVisualizer(TestCase):
    def test_init(self):
        # Initialize the object with no data
        lsp = LSV()
        self.assertTrue(
            all(lsp.x_data_lsp != None)
        )  # Check that the x_data_lsp is not None
        self.assertTrue(
            all(lsp.y_data_lsp != None)
        )  # Check that the y_data_lsp is not None

    def test_init_with_data(self):
        # Initialize the object with data
        x_data_lsp = np.array([1, 2, 3, 4, 5])
        y_data_lsp = np.array([1, 2, 3, 4, 5])
        lsp = LSV(x_data_lsp, y_data_lsp)
        self.assertEqual(np.array_equal(lsp.x_data_lsp, x_data_lsp), True)
        self.assertEqual(np.array_equal(lsp.y_data_lsp, y_data_lsp), True)

    def test_exceptionInit(self):
        # Initialize the object with data of different sizes
        x_data_lsp = np.array([1, 2, 3, 4, 5])
        y_data_lsp = np.array([1, 2, 3, 4])
        self.assertRaises(Exception, LSV, x_data_lsp, y_data_lsp)

        # len(x_data_lsp) < 2
        x_data_lsp = np.array([1])
        y_data_lsp = np.array([1])
        self.assertRaises(Exception, LSV, x_data_lsp, y_data_lsp)

    def test_run(self):
        # Run the object with no data
        lsp = LSV()
        # No exception should be raised
        lsp.run()

    def test_select_poly(self):
        # Run the object with no data
        lsp = LSV()
        lsp.run()

        lsp.function_type.value = "Polynomial"  # No Exception should be raised
        self.assertTrue(
            len(lsp.remarks.value) > 1
        )  # Check that the remarks are not empty))

        # Select the polynomial degree
        for i in range(lsp.polynomial_degree.max):
            lsp.polynomial_degree.value = i  # No Exception should be raised

        lsp.polynomial_degree.value = lsp.polynomial_degree.max + 1
        self.assertTrue(
            lsp.polynomial_degree.value == lsp.polynomial_degree.max
        )  # Check that the degree is not greater than the max

    def test_select_data(self):
        # Run the object with no data
        lsp = LSV()
        lsp.run()

        lsp.function_type.value = "Only data"
        self.assertTrue(len(lsp.remarks.value) == 0)  # Check that the remarks are empty

    def test_select_exp(self):
        # Run the object with no data
        lsp = LSV()
        lsp.run()

        lsp.function_type.value = "Exponential"  # No Exception should be raised
        self.assertTrue(
            len(lsp.remarks.value) > 1
        )  # Check that the remarks are not empty))

    def test_select_sinCos(self):
        # Run the object with no data
        lsp = LSV()
        lsp.run()

        lsp.function_type.value = "Sines & Cosines"
        self.assertTrue(
            len(lsp.remarks.value) > 1
        )  # Check that the remarks are not empty))

        # Select the Sines & Cosines degree
        for i in range(lsp.sine_cosine_degree.max):
            lsp.sine_cosine_degree.value = i

        lsp.sine_cosine_degree.value = lsp.sine_cosine_degree.max + 1
        self.assertTrue(
            lsp.sine_cosine_degree.value == lsp.sine_cosine_degree.max
        )  # Check that the degree is not greater than the max
