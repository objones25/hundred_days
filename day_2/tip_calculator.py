def main():
    print("Welcome to the tip calculator.")
    bill = float(input("What was the total bill? $"))
    tip_percentage = int(input("What percentage tip would you like to give? 10, 12, or 15? "))
    people = int(input("How many people to split the bill? "))

    tip = bill * (tip_percentage / 100)
    total = bill + tip
    split = total / people

    print(f"Each person should pay: ${split:.2f}")

if __name__ == "__main__":
    main()