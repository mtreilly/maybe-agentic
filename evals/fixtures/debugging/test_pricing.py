import unittest
from pricing import discounted_total

class PricingTest(unittest.TestCase):
    def test_half_price(self):
        self.assertEqual(discounted_total(1000, 50), 500)

if __name__ == '__main__':
    unittest.main()
