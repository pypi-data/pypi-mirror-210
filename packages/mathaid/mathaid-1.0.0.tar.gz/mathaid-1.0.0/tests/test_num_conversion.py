import unittest
from mathaid import dec_to_bin, bin_to_dec, dec_to_hex, hex_to_dec, dec_to_oct, oct_to_dec

class NumberConversionTestCase(unittest.TestCase):
    def test_dec_to_bin(self):
        test_cases = [
            (0, "0"),
            (10, "1010"),
            (27, "11011"),
            (123456, "11110001001000000"),
        ]

        for num, expected_result in test_cases:
            result = dec_to_bin(num)
            self.assertEqual(result, expected_result)

    def test_bin_to_dec(self):
        test_cases = [
            ("0", 0),
            ("1010", 10),
            ("11011", 27),
            ("11110001001000000", 123456),
        ]

        for binary, expected_result in test_cases:
            result = bin_to_dec(binary)
            self.assertEqual(result, expected_result)

    def test_dec_to_hex(self):
        test_cases = [
            (0, "0"),
            (10, "a"),
            (27, "1b"),
            (123456, "1e240"),
        ]

        for num, expected_result in test_cases:
            result = dec_to_hex(num)
            self.assertEqual(result, expected_result)

    def test_hex_to_dec(self):
        test_cases = [
            ("0", 0),
            ("a", 10),
            ("1b", 27),
            ("1e240", 123456),
        ]

        for hexadecimal, expected_result in test_cases:
            result = hex_to_dec(hexadecimal)
            self.assertEqual(result, expected_result)

    def test_dec_to_oct(self):
        test_cases = [
            (0, "0"),
            (10, "12"),
            (27, "33"),
            (123456, "361100"),
        ]

        for num, expected_result in test_cases:
            result = dec_to_oct(num)
            self.assertEqual(result, expected_result)

    def test_oct_to_dec(self):
        test_cases = [
            ("0", 0),
            ("12", 10),
            ("33", 27),
            ("361100", 123456),
        ]

        for octal, expected_result in test_cases:
            result = oct_to_dec(octal)
            self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
