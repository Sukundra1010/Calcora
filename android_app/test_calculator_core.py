import unittest

from calculator_core import calculate


class CalculatorTests(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(calculate(8, "+", 5), 13)
        self.assertEqual(calculate(8, "-", 5), 3)
        self.assertEqual(calculate(8, "*", 5), 40)
        self.assertEqual(calculate(8, "/", 4), 2)

    def test_sign_and_percent(self):
        self.assertEqual(calculate(8, "sign"), -8)
        self.assertEqual(calculate(8, "percent"), 0.08)

    def test_division_by_zero(self):
        with self.assertRaisesRegex(ValueError, "Cannot divide by zero"):
            calculate(8, "/", 0)


if __name__ == "__main__":
    unittest.main()
