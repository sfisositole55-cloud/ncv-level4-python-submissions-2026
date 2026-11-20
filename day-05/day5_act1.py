
class Product:
    VAT_RATE = 0.15

    def __init__(self, code, name, price):
        self.code = code
        self.name = name

        if price < 0:
            raise ValueError("Price cannot be negative.")

        self.price = price

    def __str__(self):
        return f"{self.code} - {self.name}: R{self.price:.2f}"

    def calc_vat(self):
        return self.price * self.VAT_RATE

    def price_including_vat(self):
        return self.price + self.calc_vat()

    def apply_discount(self, percentage):
        discount = self.price * percentage / 100
        return self.price - discount

    # NEW METHOD
    def price_after_discount_including_vat(self, percentage):
        discounted_price = self.apply_discount(percentage)
        vat = discounted_price * self.VAT_RATE

        return discounted_price + vat


def main():
    product1 = Product("P001", "Keyboard", 450.00)
    product2 = Product("P002", "Mouse", 250.00)

    print(product1)
    print(product2)

    print("VAT:", product1.calc_vat())

    print("Price including VAT:",
          product1.price_including_vat())

    print("Price after 10% discount:",
          product1.apply_discount(10))

    print("Final price after discount and VAT:",
          product1.price_after_discount_including_vat(10))


main()
