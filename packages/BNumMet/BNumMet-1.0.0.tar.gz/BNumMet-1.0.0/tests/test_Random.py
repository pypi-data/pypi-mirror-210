from BNumMet import Random
from unittest import TestCase
import numpy as np
from BNumMet.Visualizers.RandomVisualizer import RandomVisualizer


class test_Random(TestCase):
    test_label = "Random Number Generator"

    def test_lehmers_start(self):
        Random.clear_lehmers_vars()
        # Tests that Lehmers Variables are initialized to None
        self.assertEqual(Random.lehmers_vars["a"], None)
        self.assertEqual(Random.lehmers_vars["c"], None)
        self.assertEqual(Random.lehmers_vars["m"], None)
        self.assertEqual(Random.lehmers_vars["x"], None)

    def test_lehmers_init(self):
        # Tests that Lehmers Variables are initialized correctly
        Random.clear_lehmers_vars()
        Random.lehmers_init(2, 3, 5, 1)
        self.assertEqual(Random.lehmers_vars["a"], 2)
        self.assertEqual(Random.lehmers_vars["c"], 3)
        self.assertEqual(Random.lehmers_vars["m"], 5)
        self.assertEqual(Random.lehmers_vars["x"], 1)
        Random.clear_lehmers_vars()

    def test_lehmers_default(self):
        # Tests that Lehmers Variables are initialized to default values
        Random.clear_lehmers_vars()
        Random.lehmers_rand()
        self.assertEqual(Random.lehmers_vars["a"], 7**5)
        self.assertEqual(Random.lehmers_vars["c"], 0)
        self.assertEqual(Random.lehmers_vars["m"], 2**31 - 1)
        Random.clear_lehmers_vars()

    def test_lehmers_initFixed(self):
        # Tests that Lehmers Variables are initialized correctly
        Random.clear_lehmers_vars()
        Random.lehmers_rand(2, 3, 5, 1)
        self.assertEqual(Random.lehmers_vars["a"], 2)
        self.assertEqual(Random.lehmers_vars["c"], 3)
        self.assertEqual(Random.lehmers_vars["m"], 5)
        Random.clear_lehmers_vars()

    def test_lehmers_rand_formula(self):
        arr = [1]
        maxIter = 100
        for i in range(maxIter):
            aux = Random.lehmers_rand(a=2**16 + 3, m=2**31, c=0, x=arr[-1])
            if len(arr) >= 3:
                lehmerFormula = (
                    6 * arr[-1] - 9 * arr[-2]
                ) % 1  # Test Xn = (6Xn-1 - 9Xn-2)
                self.assertEqual(lehmerFormula, aux)
            arr.append(aux)

    def test_marsaglia_start(self):
        Random.clear_marsaglia_vars()
        # Tests that Marsaglia Variables are initialized to None
        self.assertEqual(Random.marsaglia_vars["base"], None)
        self.assertEqual(Random.marsaglia_vars["lag_r"], None)
        self.assertEqual(Random.marsaglia_vars["lag_s"], None)
        self.assertEqual(Random.marsaglia_vars["carry"], None)
        self.assertEqual(Random.marsaglia_vars["args"], None)

    def test_marsaglia_init(self):
        # Tests that Marsaglia Variables are initialized correctly
        Random.clear_marsaglia_vars()
        Random.marsaglia_init(2, 2, 1, 1, seed_tuple=(1, 2))
        self.assertEqual(Random.marsaglia_vars["base"], 2)
        self.assertEqual(Random.marsaglia_vars["lag_r"], 2)
        self.assertEqual(Random.marsaglia_vars["lag_s"], 1)
        self.assertEqual(Random.marsaglia_vars["carry"], 1)
        self.assertEqual(Random.marsaglia_vars["args"], [1, 2])

        Random.clear_marsaglia_vars()
        # ValueError: seedTuple must be a tuple of length 2
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 3, 5, 1, seed_tuple=1)
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 3, 5, 1, seed_tuple=(1, 2, 3))
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 3, 5, 1, seed_tuple=(1,))

        # ValueError: lag_r and lag_s must be greater than 0
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 0, 5, 1, seed_tuple=(1, 2))
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 3, 0, 1, seed_tuple=(1, 2))

        # ValueError: lag_r must be greater than or equal to lag_s
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 2, 3, 1, seed_tuple=(1, 2))

        # ValueError: carry must be 0 or 1
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 5, 3, 24, seed_tuple=(1, 2))

        # ValueError: base must be greater than 0
        with self.assertRaises(ValueError):
            Random.marsaglia_init(0, 5, 3, 1, seed_tuple=(1, 2))

        # Check if lag_r and lag_s are greater than 0
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, -1, 5, 1, seed_tuple=(1, 2))
        with self.assertRaises(ValueError):
            Random.marsaglia_init(2, 3, 0, 1, seed_tuple=(1, 2))

    def test_marsaglia_default(self):
        # Tests that Marsaglia Variables are initialized to default values
        Random.clear_marsaglia_vars()
        Random.marsaglia_rand()
        self.assertEqual(Random.marsaglia_vars["base"], 2**31 - 1)
        self.assertEqual(Random.marsaglia_vars["lag_r"], 19)
        self.assertEqual(Random.marsaglia_vars["lag_s"], 7)
        self.assertEqual(Random.marsaglia_vars["carry"], 1)
        Random.clear_marsaglia_vars()

    def test_marsaglia_initFixed(self):
        # Tests that Marsaglia Variables are initialized correctly
        Random.clear_marsaglia_vars()
        Random.marsaglia_rand(2, 2, 1, 1, seed_tuple=(1, 2))
        self.assertEqual(Random.marsaglia_vars["base"], 2)
        self.assertEqual(Random.marsaglia_vars["lag_r"], 2)
        self.assertEqual(Random.marsaglia_vars["lag_s"], 1)
        self.assertEqual(Random.marsaglia_vars["carry"], 1)
        self.assertEqual(Random.marsaglia_vars["args"][0], 2)
        Random.clear_marsaglia_vars()

    def test_marsaglia_rand_formula(self):
        testArr = [
            0.0,
            1,
            0.9,
            0.1,
            0.7,
            0.4,
            0.2,
            0.2,
            0.0,
            0.2,
            0.8,
            0.3,
            0.4,
            0.9,
        ]  # According to Bibliography
        resArr = [0, 1]
        Random.clear_marsaglia_vars()
        for _ in range(len(testArr) - 2):
            resArr.append(
                Random.marsaglia_rand(
                    base=10, lag_r=2, lag_s=1, carry=0, seed_tuple=(0, 1)
                )
            )
            self.assertEqual(testArr[: len(resArr)], resArr)

    def test_mt_start(self):
        Random.clear_mt_vars()
        # Tests that Mersenne Variables are initialized to None
        mt_vars = {
            "N": None,  # N
            "M": None,  # M
            "MATRIX_A": None,  # MATRIX_A
            "UPPER_MASK": None,  # UPPER_MASK
            "LOWER_MASK": None,  # LOWER_MASK
            "TEMPERING_MASK_B": None,  # TEMPERING_MASK_B
            "TEMPERING_MASK_C": None,  # TEMPERING_MASK_C
            "mt": None,  # mt
            "mti": None,  # mti
        }
        self.assertEqual(Random.mt_vars, mt_vars)

        Random.clear_mt_vars()
        # Tests that Mersenne Variables are initialized correctly
        Random.sgenrand(1)
        self.assertEqual(Random.mt_vars["N"], 624)
        self.assertEqual(Random.mt_vars["M"], 397)
        self.assertEqual(Random.mt_vars["MATRIX_A"], 0x9908B0DF)
        self.assertEqual(Random.mt_vars["UPPER_MASK"], 0x80000000)
        self.assertEqual(Random.mt_vars["LOWER_MASK"], 0x7FFFFFFF)
        self.assertEqual(Random.mt_vars["TEMPERING_MASK_B"], 0x9D2C5680)
        self.assertEqual(Random.mt_vars["TEMPERING_MASK_C"], 0xEFC60000)
        self.assertEqual(Random.mt_vars["mt"][0], 1 & 0xFFFFFFFF)
        self.assertEqual(Random.mt_vars["mti"], 624)  # mti

    def test_mt_init(self):
        Random.clear_mt_vars()
        # Tests that Mersenne Variables are initialized correctly
        Random.genrand(1)
        self.assertEqual(Random.mt_vars["N"], 624)
        self.assertEqual(Random.mt_vars["M"], 397)
        self.assertEqual(Random.mt_vars["MATRIX_A"], 0x9908B0DF)
        self.assertEqual(Random.mt_vars["UPPER_MASK"], 0x80000000)
        self.assertEqual(Random.mt_vars["LOWER_MASK"], 0x7FFFFFFF)
        self.assertEqual(Random.mt_vars["TEMPERING_MASK_B"], 0x9D2C5680)
        self.assertEqual(Random.mt_vars["TEMPERING_MASK_C"], 0xEFC60000)
        self.assertNotEqual(
            Random.mt_vars["mt"][0], 1 & 0xFFFFFFFF
        )  # Not equal because it has executed the generator
        self.assertEqual(
            Random.mt_vars["mti"], 1
        )  # Must be 1 because it has executed the generator

        Random.clear_mt_vars()
        # Initialize not with Int
        with self.assertRaises(ValueError):
            Random.genrand("1")

    def test_mt_randomness(self):
        from nistrng import (
            pack_sequence,
            check_eligibility_all_battery,
            run_all_battery,
            SP800_22R1A_BATTERY,
        )

        Random.clear_mt_vars()

        sequence = np.array(
            [Random.genrand() * 0xFFFFFFFF for i in range(100)], dtype=np.uint64
        )

        binary_sequence: np.ndarray = pack_sequence(sequence)

        # Check the eligibility of the test and generate an eligible battery from the default NIST-sp800-22r1a battery
        eligible_battery: dict = check_eligibility_all_battery(
            binary_sequence, SP800_22R1A_BATTERY
        )

        # Test the sequence on the eligible tests
        results = run_all_battery(binary_sequence, eligible_battery, False)
        # Print results one by one
        results = [result.passed for result, _ in results if result.passed]

        self.assertGreaterEqual(len(results), 9)


class test_RandomVisualizer(TestCase):
    def test_initiate(self):
        # Tests that the RandomVisualizer is initiated correctly without any arguments
        # No Exceptions should be raised
        rv = RandomVisualizer()

        self.assertTrue(len(rv.generated_numbers) == 0)
        self.assertEqual(rv.iterations, 100)

        random_float = rv.random_generator()
        self.assertGreaterEqual(random_float, 0)
        self.assertLessEqual(random_float, 1)

    def test_initiate_with_args(self):
        # Tests that the RandomVisualizer is initiated correctly with arguments
        # No Exceptions should be raised
        rv = RandomVisualizer(random_generator=Random.marsaglia_rand)

        self.assertTrue(len(rv.generated_numbers) == 0)
        self.assertEqual(rv.iterations, 100)

        random_float = rv.random_generator()
        self.assertGreaterEqual(random_float, 0)
        self.assertLessEqual(random_float, 1)

    def test_run_no_exception(self):
        # Tests that the RandomVisualizer is initiated correctly without any arguments
        # No Exceptions should be raised
        rv = RandomVisualizer()
        rv.run()

    def test_play(self):
        # Tests that the RandomVisualizer is initiated correctly without any arguments
        # No Exceptions should be raised
        rv = RandomVisualizer()
        rv.run()
        rv.run_button.click()

        self.assertTrue(rv.current_value - np.pi < 0.7)

    def test_int_text(self):
        # Tests that the RandomVisualizer is initiated correctly without any arguments
        # No Exceptions should be raised
        rv = RandomVisualizer()
        rv.run()

        rv.iterations_widget.value = 10000
        self.assertEqual(
            rv.iterations_widget.value, 10000
        )  # Should be 1000 because of the max value

        rv.iterations_widget.value = 0
        self.assertEqual(
            rv.iterations_widget.value, 1
        )  # Should be 1 because of the min value
