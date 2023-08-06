from BNumMet.NonLinear import *
from BNumMet.Visualizers.NonLinearVisualizer import NonLinearVisualizer
import numpy as np
from unittest import TestCase


class test_Roots(TestCase):
    def test_bisect(self):
        """
        Test the bisection method
        """
        f = lambda x: x**2 - 1
        x = bisect(f, [0, 2])
        x1, iters = bisect(f, [0, 2], iters=True)
        self.assertTrue(np.isclose(x, 1))
        self.assertTrue(np.isclose(x1, 1))

    def test_secant(self):
        """
        Test the secant method
        """
        f = lambda x: x**2 - 1
        x = secant(f, [0, 2])
        x1, iters = secant(f, [0, 2], iters=True)
        self.assertTrue(np.isclose(x, 1))
        self.assertTrue(np.isclose(x1, 1))

    def test_newton(self):
        """
        Test the Newton method
        """
        f = lambda x: x**2 - 1
        fprime = lambda x: 2 * x
        x = newton(f, fprime, 3)
        x1, iters = newton(f, fprime, 3, iters=True)
        self.assertTrue(np.isclose(x, 1))
        self.assertTrue(np.isclose(x1, 1))

    def test_zBrentDekker(self):
        """
        Test the zBrentDekker method
        """
        f = lambda x: x**2 - 1
        x0 = zBrentDekker(f, [0, 2])
        x, iters = zBrentDekker(f, [0, 2], iters=True)
        x1, iters1, steps = zBrentDekker(f, [0, 2], iters=True, steps=True)
        x2, steps = zBrentDekker(f, [0, 2], iters=False, steps=True)
        print(x, iters)
        self.assertTrue(np.isclose(x0, 1))
        self.assertTrue(np.isclose(x, 1))
        self.assertTrue(np.isclose(x1, 1))
        self.assertTrue(iters == iters1)
        self.assertTrue(np.isclose(x2, 1))

    def test_IQI(self):
        """
        Test the IQI method
        """
        f = lambda x: x**2 - 1
        x = IQI(f, [0, 2 / 3, 2])
        x1, iters = IQI(f, [0, 2 / 3, 2], iters=True)
        self.assertTrue(np.isclose(x, 1))
        self.assertTrue(np.isclose(x1, 1))

    def test_SameSign(self):
        """
        Test if in (a,b) with both f(a),f(b) >0 or <0 then ValueError is raised in all methods

        """
        f = lambda x: x**2 - 1
        methods = [bisect, secant, zBrentDekker]
        for method in methods:
            with self.assertRaises(ValueError):
                method(f, [-2, 2])

    def test_OneStep_Bisect(self):
        """
        Test if the bisect method returns the correct value after one step, this test is of critical importance, since the future zBrentDekker method is based on the bisect method
        """

        f = lambda x: x**2 - 1
        x = bisect(f, [0, 1.5], 1)
        self.assertTrue(np.isclose(x, 3 / 4))

    def test_OneStep_Secant(self):
        """
        Test if the secant method returns the correct value after one step, this test is of critical importance, since the future zBrentDekker method is based on the secant method
        """
        f = lambda x: x**2 - 1
        x = secant(f, [0, 1.5], 1)
        self.assertTrue(np.isclose(x, 2 / 3))

    def test_OneStep_Newton(self):
        """
        Test if the Newton method returns the correct value after one step
        """
        f = lambda x: x**2 - 1
        fprime = lambda x: 2 * x
        x = newton(f, fprime, 3, 1)
        self.assertTrue(np.isclose(x, 5 / 3))

    def test_OneStep_IQI(self):
        """
        Test if the IQI method returns the correct value after one step, this test is of critical importance, since the future zBrentDekker method is based on the IQI method
        """
        f = lambda x: 6 * x**2 - 2 * x**3
        x = IQI(f, [4, 4.5, 5], 1)
        print(x)
        self.assertTrue(np.isclose(x, 3.3104729014286414))

    def test_zBrentDekker_bookExamples(self):
        """
        Tests the zBrentDekker method on the examples from the reference book
        """
        f1 = (
            lambda x: 0 if abs(x) < 3.8 * 10 ** (-4) else float(x * np.exp(-1 / x**2))
        )
        f2 = (
            lambda x: float(np.exp(x))
            if x > -(10**6)
            else float(np.exp(-(10**6)) - (x + 10**6) ** 2)
        )
        tests = [  # (f, interval, tol, expectedIterations)
            (lambda x: x**9, [-1, 1.1], 10 ** (-9), 81),
            (lambda x: x**9, [-1, 4.0], 10 ** (-20), 189),
            (lambda x: x**19, [-1, 4.0], 10 ** (-20), 195),
            (f1, [-1, 4], 10 ** (-20), 33),
            (f2, [-1001200, 0], 10 ** (-20), 79),
        ]
        for test in tests:
            x, iters = zBrentDekker(test[0], test[1], tol=test[2], iters=True)

            self.assertTrue(np.isclose(test[0](x), 0))
            self.assertLessEqual(iters, test[3])


class Test_NonLinearVisualizer(TestCase):
    def test_no_param_init(self):
        """
        Tests if NonLinearVisualizer is initialized correctly without parameters (i.e. default values are used)
        """

        self.nonLinearVisualizer = NonLinearVisualizer()
        self.nonLinearVisualizer.run()

        fun = lambda x: (x - 1) * (x - 4) * np.exp(-x)
        interval = (0, 3)

        x = np.linspace(interval[0], interval[1], 100)

        self.assertTrue(np.allclose(self.nonLinearVisualizer.f(x), fun(x)))
        self.assertEqual(self.nonLinearVisualizer.a, interval[0])
        self.assertEqual(self.nonLinearVisualizer.b, interval[1])

    def test_acts_as_BrenttDekker(self):
        """
        The NonLinearVisualizer should act as the BrentDekker method if help is followed
        """
        f = lambda x: x**2 - 1
        interval = (0, 2)
        tol = 1e-20
        x, itersbrentt, stack = zBrentDekker(
            f, interval, iters=True, steps=True, tol=tol
        )
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        iters = 0
        guiStack = []
        while nonLinearVisualizer.hint_step != None:
            if nonLinearVisualizer.hint_step == "Bisection":
                guiStack.append("Bisection")
                nonLinearVisualizer.bisect_button.click()
            elif nonLinearVisualizer.hint_step == "Secant":
                guiStack.append("Secant")
                nonLinearVisualizer.secant_button.click()
            elif nonLinearVisualizer.hint_step == "IQI":
                guiStack.append("IQI")
                nonLinearVisualizer.iqi_button.click()
            iters += 1

            if iters > itersbrentt:
                self.fail(
                    "NonLinearVisualizer did not converge to the same value as zBrentDekker"
                )

        self.assertEqual(len(guiStack), len(stack))
        self.assertEqual(guiStack, stack)

    def test_revertStep(self):
        """
        Tests if the revertStep method works correctly
        """
        f = lambda x: x**2 - 1
        interval = (0, 2)
        tol = 1e-20
        x, iters, stack = zBrentDekker(f, interval, iters=True, steps=True, tol=tol)
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        # Perform all steps and store them in a stack
        guiStack = []
        while nonLinearVisualizer.hint_step != None:
            guiStack.append(nonLinearVisualizer.hint_step)
            if nonLinearVisualizer.hint_step == "Bisection":
                nonLinearVisualizer.bisect_button.click()
            elif nonLinearVisualizer.hint_step == "Secant":
                nonLinearVisualizer.secant_button.click()
            elif nonLinearVisualizer.hint_step == "IQI":
                nonLinearVisualizer.iqi_button.click()

        # Revert the last step and check if the hintStep is the same as the future step in the stack
        i = len(guiStack) - 1
        while nonLinearVisualizer.revert_stack != []:
            nonLinearVisualizer.revert_button.click()
            i -= 1
            self.assertTrue(nonLinearVisualizer.hint_step == stack[i + 1])

    def test_reset(self):
        """
        Tests if the reset method works correctly
        """
        f = lambda x: x**2 - 1
        interval = (0, 2)
        tol = 1e-20
        x, iters, stack = zBrentDekker(f, interval, iters=True, steps=True, tol=tol)
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        # Perform all steps and store them in a stack
        guiStack = []
        while nonLinearVisualizer.hint_step != None:
            guiStack.append(nonLinearVisualizer.hint_step)
            if nonLinearVisualizer.hint_step == "Bisection":
                nonLinearVisualizer.bisect_button.click()
            elif nonLinearVisualizer.hint_step == "Secant":
                nonLinearVisualizer.secant_button.click()
            elif nonLinearVisualizer.hint_step == "IQI":
                nonLinearVisualizer.iqi_button.click()

        # A Reset should revert all steps and set the hintStep to the first step in the stack
        nonLinearVisualizer.reset_button.click()
        self.assertEqual(nonLinearVisualizer.revert_stack, [])
        self.assertTrue(nonLinearVisualizer.hint_step == stack[0])

        a = nonLinearVisualizer.a
        c = nonLinearVisualizer.c
        b = nonLinearVisualizer.b

        self.assertEqual(nonLinearVisualizer.a, nonLinearVisualizer.c)
        self.assertListEqual(sorted([a, b]), list(nonLinearVisualizer.original_data))

    def test_legend_length_after_checkbox(self):
        """
        Figure Marks should be more than original after a checkbox is clicked
        """
        f = lambda x: x**2 - 1
        interval = (0, 2)
        tol = 1e-20
        x, iters, stack = zBrentDekker(f, interval, iters=True, steps=True, tol=tol)
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        og_length = len(nonLinearVisualizer.fig.marks)

        nonLinearVisualizer.bisect_checkbox.value = True
        self.assertTrue(len(nonLinearVisualizer.fig.marks) > og_length)

        nonLinearVisualizer.bisect_checkbox.value = False
        self.assertEqual(len(nonLinearVisualizer.fig.marks), og_length)

        nonLinearVisualizer.secant_checkbox.value = True
        self.assertTrue(len(nonLinearVisualizer.fig.marks) > og_length)

        self.assertTrue(
            nonLinearVisualizer.iqi_checkbox.disabled
        )  # IQI is disabled by at first step of this function
        # Perform all steps and store them in a stack
        guiStack = []
        while nonLinearVisualizer.hint_step != None:
            guiStack.append(nonLinearVisualizer.hint_step)
            if nonLinearVisualizer.hint_step == "Bisection":
                nonLinearVisualizer.bisect_button.click()
            elif nonLinearVisualizer.hint_step == "Secant":
                nonLinearVisualizer.secant_button.click()
            elif nonLinearVisualizer.hint_step == "IQI":
                self.assertFalse(nonLinearVisualizer.iqi_checkbox.disabled)
                nonLinearVisualizer.iqi_checkbox.value = True
                self.assertTrue(len(nonLinearVisualizer.fig.marks) > og_length)
                break

    def test_sign_not_guranteed(self):
        """
        Raise exception if signs are the same
        """
        f = lambda x: x**2 - 1
        interval = (2, 4)
        tol = 1e-20
        with self.assertRaises(Exception):
            zBrentDekker(f, interval, tol=tol)

    def test_sign_zero_start(self):
        """
        Already found solution at start
        """
        f = lambda x: x**2 - 1
        interval = (1, 4)
        tol = 1e-20
        x, iters, stack = zBrentDekker(f, interval, iters=True, steps=True, tol=tol)
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        self.assertEqual(x, 1)
        self.assertEqual(iters, 0)
        self.assertEqual(stack, [])

        self.assertEqual(nonLinearVisualizer.b, 1)

    def test_reset_emptyStack(self):
        """
        Test if reset works when the stack is empty (i.e. no steps have been taken)
        """
        f = lambda x: x**2 - 1
        interval = (0, 2)
        tol = 1e-20
        x, iters, stack = zBrentDekker(f, interval, iters=True, steps=True, tol=tol)
        nonLinearVisualizer = NonLinearVisualizer(f, interval, tol=tol)
        nonLinearVisualizer.run()

        # A Reset should revert all steps and set the hintStep to the first step in the stack
        nonLinearVisualizer.reset_button.click()
        self.assertEqual(nonLinearVisualizer.revert_stack, [])
        self.assertTrue(nonLinearVisualizer.hint_step == stack[0])

    def test_exception_wrongSign(self):
        """
        Tests if the exception is raised when the signs are NOT different
        """
        f = lambda x: x**2 - 1
        interval = (2, 4)
        tol = 1e-20
        with self.assertRaises(Exception):
            zBrentDekker(f, interval, tol=tol)
