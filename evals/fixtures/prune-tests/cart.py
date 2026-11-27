class Cart:
    def __init__(self, tax_rate=0.1):
        self._items = []
        self._tax_rate = tax_rate

    def add_item(self, sku: str, price_cents: int, qty: int = 1):
        if qty <= 0 or price_cents < 0:
            raise ValueError('invalid item')
        self._items.append({'sku': sku, 'price_cents': price_cents, 'qty': qty})

    def items(self):
        return [dict(item) for item in self._items]

    def subtotal_cents(self) -> int:
        return sum(item['price_cents'] * item['qty'] for item in self._items)

    def tax_cents(self) -> int:
        return round(self.subtotal_cents() * self._tax_rate)

    def total_cents(self) -> int:
        return self.subtotal_cents() + self.tax_cents()
