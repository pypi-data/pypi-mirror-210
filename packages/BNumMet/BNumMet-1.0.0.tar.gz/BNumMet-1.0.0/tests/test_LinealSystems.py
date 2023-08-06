import os
import sys
import unittest
from random import randint
from unittest import TestCase

import numpy as np
import pytest

from BNumMet.LinearSystems import (
    backward_substitution,
    forward_substitution,
    interactive_lu,
    lu,
    lu_solve,
    permute,
    qr_factorization,
    qr_solve,
)
from BNumMet.Visualizers.LUVisualizer import LUVisualizer


class test_LU(TestCase):
    def test_lu_simple(self):
        """
        Test the LU decomposition by running it on a fixed matrix and checking that the result is correct
        """
        A = np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5]])
        P, L, U = lu(A)
        # print(P@A)
        print(P)
        print(L)
        print(U)

        self.assertTrue(np.allclose(P @ A, L @ U))

    def test_lu_random(self):
        """
        Test the LU decomposition by running it on a random matrix and checking that the result is correct
        """
        A = np.random.rand(10, 10)
        P, L, U = lu(A)

        self.assertTrue(np.allclose(P @ A, L @ U), msg=f"P@A != L@U\n{P@A} != {L@U}")

    def test_lu_random_ints(self):
        """
        Test the LU decomposition by running it on a random INTEGER matrix and checking that the result is correct
        This test is useful to check that the algorithm works with integer matrices as well because the python maintains the type of the elements of the matrix when performing operations
        """
        A = np.random.randint(0, 10, (10, 10))
        P, L, U = lu(A)

        self.assertTrue(np.allclose(P @ A, L @ U), msg=f"P@A != L@U\n{P@A} != {L@U}")

    def test_lu_notSquare(self):
        """
        Test that the LU decomposition raises a ValueError when the matrix is not square
        """
        A = np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5], [1, 2, 3]])
        with self.assertRaises(ValueError):
            P, L, U = lu(A)

    def test_permute(self):
        """
        Test the permute function by running it on a fixed matrix and checking that the result is correct
        It also checks that the function does not modify the original matrix
        """
        A = np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5]])

        for i in range(A.shape[0]):
            self.assertTrue(
                np.allclose(permute(A, i, i), A)
            )  # Check trivial permutation
        self.assertTrue(
            np.allclose(
                permute(A, 0, 1), np.array([[-3, 2, 6], [10, -7, 0], [5, -1, 5]])
            )
        )  # swap 1st and 2nd rows
        self.assertFalse(
            np.allclose(A, np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5]]))
        )  # It is not the same matrix as A - initially

    def test_interactive_lu(self):
        """
        Test the interactive LU decomposition by running it on a fixed matrix and checking that the result is correct
        we do not test the visualizer here, just the algorithm, with automated pivoting (i.e. iMax = -1)
        """
        A = np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5]])
        L = np.eye(A.shape[0])
        U = A.copy()
        P = np.eye(A.shape[0])

        lastColumn = 0
        rank = 0
        while lastColumn != -1:
            P, L, U, lastColumn, rank, msg = interactive_lu(
                P, L, U, lastColumn, rank, -1
            )
            self.assertTrue(np.allclose(P @ A, L @ U))
        print(rank)
        assert rank == A.shape[0]

    def test_interactive_lu_ranks(self):
        """
        Test the interactive LU decomposition by running it on a fixed matrix and checking that the result is correct
        we do not test the visualizer here, just the algorithm, with automated pivoting (i.e. iMax = -1)
        """
        A = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        L = np.eye(A.shape[0])
        U = A.copy()
        P = np.eye(A.shape[0])

        _, _, _, _, rank, _ = interactive_lu(P, L, U, 0, 0, -1)
        self.assertTrue(rank == 0)

        A = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        L = np.eye(A.shape[0])
        U = A.copy()
        P = np.eye(A.shape[0])

        _, _, _, _, rank, _ = interactive_lu(P, L, U, 0, 0, -1)
        col = 0
        rank = 0
        while col != -1:
            P, L, U, col, rank, msg = interactive_lu(P, L, U, col, rank, -1)
            self.assertTrue(np.allclose(P @ A, L @ U))
        self.assertTrue(rank == A.shape[0])

        A = np.array([[1, 4, 7], [1, 5, 7], [1, 4, 7]])  # rank 2 on the second column
        L = np.eye(A.shape[0])
        U = A.copy()
        P = np.eye(A.shape[0])
        col = 0
        rank = 0
        while col != -1:
            P, L, U, col, rank, msg = interactive_lu(P, L, U, col, rank, -1)
            self.assertTrue(np.allclose(P @ A, L @ U))

        self.assertTrue(rank == 2)

        A = np.array([[1, 4, 7], [1, 4, 7], [1, 4, 9]])  # rank 2 on the third column
        L = np.eye(A.shape[0])
        U = A.copy()
        P = np.eye(A.shape[0])
        col = 0
        rank = 0
        while col != -1:
            P, L, U, col, rank, msg = interactive_lu(P, L, U, col, rank, -1)
            self.assertTrue(np.allclose(P @ A, L @ U))

        self.assertTrue(rank == 2)  #

    def test_forwardSubstitution(self):
        """
        Test the forward substitution algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.forwardSubstitution
        """
        L = np.array([[1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        b = np.array([1, 2, 3])
        x = np.array([1, 1.5, 1.75])

        self.assertTrue(np.allclose(forward_substitution(L, b), x))

    def test_backwardSubstitution(self):
        """
        Test the backward substitution algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.backwardSubstitution
        """
        U = np.array([[1, 2, 3], [0, 1, 2], [0, 0, 1]])
        b = np.array([1, 2, 3])
        x = np.array([0, -4, 3])

        self.assertTrue(np.allclose(backward_substitution(U, b), x))

    def test_forwardSubstitution_expceptions(self):
        """
        Test the forward substitution algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.forwardSubstitution
        """
        L = np.array([[1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        b = np.array([1, 2, 3, 4])
        x = np.array([1, 1.5, 2])
        # 1. The left hand side has more rows than the right hand side
        with self.assertRaises(ValueError, msg="b has more elements than L"):
            forward_substitution(L, b)  # b has more elements than L

        # 2. The left hand side has less rows than the right hand side
        L = np.array([[1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        b = np.array([1, 2])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="L has more rows than b"):
            forward_substitution(L, b)

        # 3. L is not lower triangular
        L = np.array([[1, 1, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        b = np.array([1, 2, 3])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="L is not lower triangular"):
            forward_substitution(L, b)

        # 4. L has a zero diagonal element
        L = np.array([[1, 0, 0], [0.5, 0, 0], [0.5, 0.5, 1]])
        b = np.array([1, 2, 3])
        x = np.array([1, 1.5, 2])
        with self.assertRaises(ValueError, msg="L has a zero diagonal element"):
            forward_substitution(L, b)

        # 5. L is not a square matrix
        L = np.array([[1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1], [0.5, 0.5, 1]])
        b = np.array([1, 2, 3, 4])
        x = np.array([1, 1.5, 2])
        with self.assertRaises(ValueError, msg="U is not a square matrix") as e:
            forward_substitution(L, b)
        # Check if e message is correct
        self.assertEqual(
            str(e.exception),
            "A is not a square matrix",
            msg="The error message is not correct",
        )

    def test_backwardSubstitution_expceptions(self):
        """
        Test the backward substitution algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.backwardSubstitution
        """
        U = np.array([[1, 2, 3], [0, 1, 2], [0, 0, 1]])
        b = np.array([1, 2, 3, 4])
        x = np.array([1, 1.5, 2])
        # 1. The left hand side has more rows than the right hand side
        with self.assertRaises(ValueError, msg="b has more elements than U"):
            backward_substitution(U, b)  # b has more elements than L

        # 2. The left hand side has less rows than the right hand side
        U = np.array([[1, 2, 3], [0, 1, 2], [0, 0, 1]])
        b = np.array([1, 2])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="U has more rows than b"):
            backward_substitution(U, b)

        # 3. U is not upper triangular
        U = np.array([[1, 2, 3], [0, 1, 2], [0, 1, 1]])
        b = np.array([1, 2, 3])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="U is not upper triangular"):
            backward_substitution(U, b)

        # 4. U has a zero diagonal element
        U = np.array([[1, 2, 3], [0, 0, 2], [0, 0, 1]])
        b = np.array([1, 2, 3])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="U has a zero diagonal element"):
            backward_substitution(U, b)

        # 5. U is not a square matrix
        U = np.array([[1, 2, 3], [0, 1, 2], [0, 0, 1], [0, 0, 0]])
        b = np.array([1, 2, 3, 4])
        x = np.array([1, 1.5, 2])

        with self.assertRaises(ValueError, msg="U is not a square matrix") as e:
            backward_substitution(U, b)
        # Check if e message is correct
        self.assertEqual(
            str(e.exception),
            "A is not a square matrix",
            msg="The error message is not correct",
        )

    def test_luSolve(self):
        """
        Test the LU decomposition algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.luSolve
        """
        A = np.array([[1, 1], [1, -1]])
        b = np.array([10, 4])
        x = np.array([7, 3])

        solution = lu_solve(A, b)

        self.assertTrue(
            np.allclose(solution, x),
            msg=f"The solution is not correct {solution} != {x}",
        )

        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        b = np.array([1, 2, 3])

        with self.assertRaises(
            ValueError, msg="A is Singular but it does not detect it!"
        ):
            lu_solve(A, b)


class Test_LinearSystems(TestCase):
    def test_qrFactorization(self):
        """
        Test the QR decomposition algorithm by running it on a fixed matrix and checking that the result is correct, testing BNumMet.qr_factorization
        """
        # Test 1: Simple 2x2 matrix
        A = np.array([[1, 2], [3, 4]])
        Q, R = qr_factorization(A)
        self.assertTrue(
            np.all(np.tril(R, -1) < 1e-15), f"R is not upper triangular {np.tril(R,-1)}"
        )
        self.assertTrue(np.allclose(A, Q @ R))

        # Test 2: Simple 3x3 matrix
        A = np.array([[1, 2, 3], [4, 8, 6], [7, 8, 9]])
        Q, R = qr_factorization(A)
        self.assertTrue(np.allclose(A, Q @ R), f"{A} != {Q @ R}")

        # Test 3: Simple 4x3 matrix
        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        Q, R = qr_factorization(A)
        self.assertTrue(np.allclose(A, Q @ R))

    def test_qrSolve(self):
        # Test case 1: Solve a 2x2 system
        A = np.array([[1, 1], [1, -1]])
        b = np.array([10, 4])
        x = np.array([7, 3])

        self.assertTrue(np.allclose(qr_solve(A, b.T), x), f"{x} != {qr_solve(A, b)}")

        # Test case 2: Solve a 3x3 system
        A = np.array([[2, -1, 0], [1, 2, -1], [0, 1, 2]])
        b = np.array([0, 2, 8])
        x = np.array([1, 2, 3])

        self.assertTrue(np.allclose(qr_solve(A, b), x), f"{x} != {qr_solve(A, b)}")

        # Test case 3: Solve a 4x4 system
        A = np.array([[2, 3, -1, 1], [1, -2, 0, -1], [2, -1, 3, -2], [1, 1, 1, 2]])
        x = np.array([2, -1, 3, 1])
        b = A @ x

        self.assertTrue(np.allclose(qr_solve(A, b), x), f"{x} != {qr_solve(A, b)}")

    def test_qrSolve_random(self):
        """
        Test the QR decomposition algorithm by running it on a random matrix and checking that the result is correct, testing BNumMet.qrSolve
        """
        for i in range(10):
            size = np.random.randint(2, 15)
            A = np.random.rand(size, size)
            x = np.ones(size)
            b = A @ x

            self.assertTrue(np.allclose(qr_solve(A, b), x), f"{x} != {qr_solve(A, b)}")

    def test_qr_lsp(self):
        """
        Test the QR solver for an mxn matrix where m > n
        """
        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        b = np.array([1, 2, 3, 4])
        x = np.array([1, 1, 1])

        # no exception should be raised
        qr_solve(A, b)


class Test_LUVisualizer(TestCase):
    def runtest_setup(self, A=None):
        """
        Run the setup for the tests of the LUVisualizer

        Parameters
        ----------
        A : np.array
            The matrix to be decomposed. If None, a fixed matrix is put
        """
        self.A = (
            np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float) if A is None else A
        )
        self.luVisualizer = LUVisualizer(self.A)
        self.luVisualizer.run()

    def test_no_param_init(self):
        """
        Test if the LUVisualizer is initialized correctly when no matrix is passed as a parameter to the constructor (i.e. A default matrix is used)
        """
        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
        self.luVisualizer = LUVisualizer()
        self.luVisualizer.run()

        self.assertTrue(np.allclose(self.luVisualizer.A, A))

    def test_initialazation(self):
        """
        Test if the LUVisualizer is initialized correctly
        """
        self.runtest_setup()
        self.assertEqual(self.luVisualizer.step, 0)
        self.assertTrue(np.allclose(self.A, self.luVisualizer.A))

        self.assertTrue(self.A.shape == self.luVisualizer.P.shape)
        self.assertTrue(self.A.shape == self.luVisualizer.L.shape)

    def test_ValueError(self):
        """
        Test if the LUVisualizer raises a ValueError when the matrix is not square
        """
        with self.assertRaises(ValueError):
            self.luVisualizer = LUVisualizer([[1, 2, 3, 4], [4, 5, 6, 4], [7, 8, 9, 4]])

    def test_step(self):
        """
        Test if step works correctly by clicking one button and then checking if the step has changed, and if the buttons have changed too
        """
        self.runtest_setup()
        # Get buttons which are not disabled
        buttons = [
            button
            for row in self.luVisualizer.buttons_matrix
            for button in row
            if not button.disabled
        ]

        # Simulate clicking one of the buttons
        buttons[0].click()

        # This should hgave changed the step and the matrix buttons
        self.assertEqual(self.luVisualizer.step, 1)
        buttons2 = [
            button
            for row in self.luVisualizer.buttons_matrix
            for button in row
            if not button.disabled
        ]
        self.assertNotEqual(buttons, buttons2)

        # The button should be disabled
        self.assertTrue(buttons[0].disabled)
        buttons[0].click()
        self.assertEqual(self.luVisualizer.step, 1)

        buttons2[0].click()
        self.assertEqual(
            self.luVisualizer.step, -1
        )  # The last is a Linear Combination --> Step +1 but it is the last step --> -1

    def test_previousStep(self):
        """
        Test if previousStep works correctly by clicking one button and then going back
        """
        self.runtest_setup()

        oldStep = (
            self.luVisualizer.step,
            self.luVisualizer.L,
            self.luVisualizer.U,
            self.luVisualizer.P,
        )

        self.assertTrue(len(self.luVisualizer.previous_steps) == 0)
        # Get buttons which are not disabled
        buttons = [
            button
            for row in self.luVisualizer.buttons_matrix
            for button in row
            if not button.disabled
        ]
        # Simulate clicking one of the buttons
        buttons[0].click()
        self.assertTrue(len(self.luVisualizer.previous_steps) == 1)

        self.luVisualizer.previous_step(None)
        self.assertEqual(self.luVisualizer.step, oldStep[0])
        self.assertTrue(np.allclose(self.luVisualizer.L, oldStep[1]))
        self.assertTrue(np.allclose(self.luVisualizer.U, oldStep[2]))
        self.assertTrue(np.allclose(self.luVisualizer.P, oldStep[3]))

    def test_reset(self):
        """
        Test reset button by clicking all buttons and then reset
        It should reset the step and the matrices to the initial values
        """
        self.runtest_setup()

        buttons = [
            button
            for row in self.luVisualizer.buttons_matrix
            for button in row
            if not button.disabled
        ]
        while len(buttons) > 0:
            buttons[0].click()
            buttons = [
                button
                for row in self.luVisualizer.buttons_matrix
                for button in row
                if not button.disabled
            ]

        # All buttons should be disabled
        self.assertTrue(
            all(
                [
                    button.disabled
                    for row in self.luVisualizer.buttons_matrix
                    for button in row
                ]
            )
        )

        self.luVisualizer.reset(None)
        self.assertEqual(self.luVisualizer.step, 0)
        self.assertTrue(np.allclose(self.luVisualizer.L, np.eye(self.A.shape[0])))
        self.assertTrue(np.allclose(self.luVisualizer.U, self.A))
        self.assertTrue(np.allclose(self.luVisualizer.P, np.eye(self.A.shape[0])))
        self.assertTrue(
            any(
                [
                    not button.disabled
                    for row in self.luVisualizer.buttons_matrix
                    for button in row
                ]
            )
        )

    def test_interactive_lu_proccess(self):
        """
        Test the interactive LU proccess:
        1. Generate a random matrix A (10x10)
        2. Run the interactive LU proccess

        for each step:
            3. Click a random button which is not disabled
            4. Check that P@A = L@U
        """
        self.runtest_setup(np.random.rand(10, 10))
        P = self.luVisualizer.P
        L = self.luVisualizer.L
        U = self.luVisualizer.U
        A = self.luVisualizer.A
        for i in range(self.A.shape[0]):
            buttons = [
                button
                for row in self.luVisualizer.buttons_matrix
                for button in row
                if not button.disabled
            ]
            if len(buttons) == 0:
                break
            buttons[randint(0, len(buttons) - 1)].click()

            P = self.luVisualizer.P
            L = self.luVisualizer.L
            U = self.luVisualizer.U
            self.assertTrue(
                np.allclose(
                    P @ A,
                    L @ U,
                ),
                msg=f"P@A != L@U\n{P@A} != {L@U}",
            )

        endButtons = self.luVisualizer.buttons_matrix
        for row in endButtons:
            for button in row:
                self.assertTrue(button.disabled)
