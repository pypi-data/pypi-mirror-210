import unittest
from mathaid import random_prime, is_prime

class RandomPrimeTestCase(unittest.TestCase):
    def test_random_prime_within_range(self):
        start = 10
        end = 100
        prime = random_prime(start, end)
        self.assertTrue(is_prime(prime))
        self.assertGreaterEqual(prime, start)
        self.assertLess(prime, end)

    def test_random_prime_default_range(self):
        prime = random_prime()
        self.assertTrue(is_prime(prime))

    def test_random_prime_invalid_range(self):
        with self.assertRaises(ValueError):
            random_prime(100, 10)

    def test_is_prime(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15]
        
        for prime in primes:
            self.assertTrue(is_prime(prime))

        for non_prime in non_primes:
            self.assertFalse(is_prime(non_prime))

if __name__ == '__main__':
    unittest.main()
