VAT_RATE = 0.14


def amount_due(facility_code, hours):
    
    if facility_code == "squa":
        rate = 13.00
    elif facility_code == "swim":
        rate = 12.00
    elif facility_code == "gym":
        rate = 11.00
    else:  
        rate = 8.00

    return rate * hours


def final_amount_due(amount):
    
    return amount + amount * VAT_RATE


def display(name, facility_code, hours, amount, final_amount):
    
    line = "=" * 36
    print()
    print(line)
    print("      TEKSONIC FITNESS HOUSE")
    print("          PAYMENT SLIP")
    print(line)
    print(f"{'Customer name':<22}{name}")
    print(f"{'Facility code':<22}{facility_code}")
    print(f"{'Hours':<22}{hours}")
    print("-" * 36)
    print(f"{'Amount before VAT':<22}R{amount:>8.2f}")
    print(f"{'Total incl. 14% VAT':<22}R{final_amount:>8.2f}")
    print(line)
    print("       Thank you for your visit!")
    print(line)


def process_payment():
    name = input("Enter customer name: ")
    facility_code = input("Enter facility code (squa, swim, gym, wei): ").strip().lower()
    hours = float(input("Enter number of hours: "))

    amount = amount_due(facility_code, hours)
    final_amount = final_amount_due(amount)
    display(name, facility_code, hours, amount, final_amount)


process_payment()