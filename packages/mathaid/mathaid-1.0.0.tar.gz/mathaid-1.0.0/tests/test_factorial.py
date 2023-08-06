import unittest
from mathaid import factorial

class FactorialTestCase(unittest.TestCase):
    def test_factorial(self):
        # Test factorial for different values
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(10), 3628800)
        
    def test_negative_input(self):
        # Test factorial for negative input
        with self.assertRaises(ValueError):
            factorial(-5)
    
if __name__ == '__main__':
    unittest.main()
