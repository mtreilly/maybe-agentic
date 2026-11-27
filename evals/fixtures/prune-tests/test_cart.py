import unittest
from cart import Cart


class CartTests(unittest.TestCase):
    def test_add_item_internal_array(self):
        cart = Cart()
        cart.add_item('book-1', 1000, 2)
        self.assertEqual(cart._items[0]['sku'], 'book-1')
        self.assertEqual(cart._items[0]['qty'], 2)

    def test_total_with_tax(self):
        cart = Cart(tax_rate=0.1)
        cart.add_item('book-1', 1000, 2)
        self.assertEqual(cart.total_cents(), 2200)

    def test_total_with_tax_duplicate(self):
        cart = Cart(tax_rate=0.1)
        cart.add_item('book-1', 1000, 2)
        self.assertEqual(cart.total_cents(), 2200)

    def test_rejects_non_positive_qty(self):
        cart = Cart()
        with self.assertRaises(ValueError):
            cart.add_item('book-1', 1000, 0)


if __name__ == '__main__':
    unittest.main()
