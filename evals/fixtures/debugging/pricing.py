def discounted_total(subtotal_cents, percent):
    if not percent or percent < 0 or percent > 100:
        raise ValueError('discount must be between 0 and 100')
    return round(subtotal_cents * (100 - percent) / 100)
