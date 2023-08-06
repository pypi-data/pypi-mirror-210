import unittest
from mathaid import lcm, hcf

class LCMandHCFTestCase(unittest.TestCase):
    def test_lcm(self):
        # Test cases with expected LCM values
        test_cases = [
            (3, 5, 15),
            (12, 18, 36),
            (7, 13, 91),
            (17, 23, 391),
            (9, 15, 45),
        ]

        # Perform the tests
        for a, b, expected_lcm in test_cases:
            result = lcm(a, b)
            self.assertEqual(result, expected_lcm)

    def test_hcf(self):
        # Test cases with expected HCF values
        test_cases = [
            (8, 12, 4),
            (54, 24, 6),
            (81, 27, 27),
            (17, 23, 1),
            (48, 60, 12),
        ]

        # Perform the tests
        for a, b, expected_hcf in test_cases:
            result = hcf(a, b)
            self.assertEqual(result, expected_hcf)

if __name__ == '__main__':
    unittest.main()
