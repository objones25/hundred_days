class MenuItem:
    """Models each menu item."""
    def __init__(self, name, water, milk, coffee, cost):
        self.name = name
        self.cost = cost
        self.ingredients = {
            "water": water,
            "milk": milk,
            "coffee": coffee
        }

class Menu:
    """Models the Menu with drinks."""
    def __init__(self):
        self.menu = {
            "espresso": MenuItem(name="espresso", water=50, milk=0, coffee=18, cost=1.5),
            "latte": MenuItem(name="latte", water=200, milk=150, coffee=24, cost=2.5),
            "cappuccino": MenuItem(name="cappuccino", water=250, milk=100, coffee=24, cost=3.0),
        }

    def get_items(self):
        """Returns all the names of the available menu items"""
        return '/'.join(list(self.menu.keys()))

    def find_drink(self, order_name):
        """Searches the menu for a particular drink by name. Returns that item if it exists, otherwise returns None"""
        try:
            return self.menu[order_name]
        except KeyError:
            print(f"Sorry, we don't have {order_name}.")
            return None

class MoneyMachine:
    """Handles all payment operations."""
    COIN_VALUES = {
        "quarters": 0.25,
        "dimes": 0.10,
        "nickles": 0.05,
        "pennies": 0.01
    }

    def __init__(self):
        self.profit = 0
        self.money_received = 0

    def report(self):
        """Prints the current profit"""
        print(f"Money: ${self.profit:.2f}")

    def process_coins(self):
        """Returns the total calculated from coins inserted."""
        print("Please insert coins.")
        for coin in self.COIN_VALUES:
            self.money_received += int(input(f"How many {coin}?: ")) * self.COIN_VALUES[coin]
        return self.money_received

    def make_payment(self, cost):
        """Returns True when payment is accepted, or False if insufficient."""
        self.process_coins()
        if self.money_received >= cost:
            change = round(self.money_received - cost, 2)
            if change > 0:
                print(f"Here is ${change:.2f} in change.")
            self.profit += cost
            self.money_received = 0
            return True
        else:
            print("Sorry that's not enough money. Money refunded.")
            self.money_received = 0
            return False

class CoffeeMaker:
    """Models the machine that makes the coffee"""
    def __init__(self):
        self.resources = {
            "water": 300,
            "milk": 200,
            "coffee": 100,
        }

    def report(self):
        """Prints a report of all resources."""
        print(f"Water: {self.resources['water']}ml")
        print(f"Milk: {self.resources['milk']}ml")
        print(f"Coffee: {self.resources['coffee']}g")

    def is_resource_sufficient(self, drink):
        """Returns True when order can be made, False if ingredients are insufficient."""
        for item, amount in drink.ingredients.items():
            if self.resources[item] < amount:
                print(f"Sorry there is not enough {item}.")
                return False
        return True

    def make_coffee(self, order):
        """Deducts the required ingredients from the resources."""
        for item, amount in order.ingredients.items():
            self.resources[item] -= amount
        print(f"Here is your {order.name} ☕️. Enjoy!")

class CoffeeMachineProgram:
    """Main program that coordinates all components"""
    def __init__(self):
        self.money_machine = MoneyMachine()
        self.coffee_maker = CoffeeMaker()
        self.menu = Menu()

    def run(self):
        is_on = True
        while is_on:
            options = self.menu.get_items()
            choice = input(f"What would you like? ({options}): ")
            if choice == "off":
                is_on = False
            elif choice == "report":
                self.coffee_maker.report()
                self.money_machine.report()
            else:
                drink = self.menu.find_drink(choice)
                if drink and self.coffee_maker.is_resource_sufficient(drink):
                    if self.money_machine.make_payment(drink.cost):
                        self.coffee_maker.make_coffee(drink)

def main():
    coffee_machine = CoffeeMachineProgram()
    coffee_machine.run()

if __name__ == "__main__":
    main()