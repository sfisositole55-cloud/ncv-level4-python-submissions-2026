import random


def generate_minutes():
  
    return random.randint(30, 180)


def calc_amount(machine_type, minutes):
   
    if machine_type == "A":
        initial_cost = 50.00
        hourly_rate = 30.00
    elif machine_type == "B":
        initial_cost = 62.50
        hourly_rate = 36.25
    else: 
        initial_cost = 74.87
        hourly_rate = 40.50

    hours = minutes / 60  
    return initial_cost + hourly_rate * hours


def calc_total_amount(amount):
    
    vat = amount * 0.14
    total = amount + vat
    return vat, total


def display_summary(payments):
   
    count = len(payments)
    combined = 0
    highest = payments[0]
    lowest = payments[0]

    for payment in payments:
        combined = combined + payment
        if payment > highest:
            highest = payment
        if payment < lowest:
            lowest = payment

    average = combined / count

    print()
    print("=" * 40)
    print("          DAILY SUMMARY")
    print("=" * 40)
    print(f"{'Customers processed':<26}{count}")
    print(f"{'Combined amount payable':<26}R{combined:.2f}")
    print(f"{'Average payment':<26}R{average:.2f}")
    print(f"{'Highest payment':<26}R{highest:.2f}")
    print(f"{'Lowest payment':<26}R{lowest:.2f}")
    print("=" * 40)


def process_payments():
    number_of_customers = int(input("Enter the number of customers to process: "))
    payments = []

    for i in range(number_of_customers):
        print()
        print(f"--- Customer {i + 1} ---")
        name = input("Enter customer name: ")
        machine_type = input("Enter machine type (A, B or C): ").strip().upper()

        minutes = generate_minutes()
        amount = calc_amount(machine_type, minutes)
        vat, total = calc_total_amount(amount)

        payments.append(total)

        print()
        print("=" * 40)
        print("        Techsonicwashy INVOICE")
        print("=" * 40)
        print(f"{'Customer name':<26}{name}")
        print(f"{'Machine type':<26}{machine_type}")
        print(f"{'Minutes used':<26}{minutes}")
        print("-" * 40)
        print(f"{'Amount before VAT':<26}R{amount:.2f}")
        print(f"{'VAT (14%)':<26}R{vat:.2f}")
        print(f"{'Total payable':<26}R{total:.2f}")
        print("=" * 40)

    display_summary(payments)


process_payments()