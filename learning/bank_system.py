# ==========================================================
# BANK ACCOUNT SYSTEM USING OOP
# ==========================================================

import random
from datetime import datetime


# ==========================================================
# BASE CLASS: BankAccount
# ==========================================================
# A class is a blueprint.
# Every BankAccount object created from this class
# will have its own owner, balance, account number,
# and transaction history.


class BankAccount:

    def __init__(self, owner):
        """
        __init__ is the constructor.
        It runs automatically when a new object is created.

        self refers to the specific object being created.
        """

        self.owner = owner
        self.balance = 0
        self.account_number = random.randint(10000000, 99999999)
        self.transactions = []  # List to store transaction history

        self._add_transaction("Account created", 0)

    # ------------------------------------------------------
    # Internal helper method to record transactions
    # ------------------------------------------------------
    def _add_transaction(self, description, amount):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append(f"{date} | {description} | Amount: {amount} | Balance: {self.balance}")

    # ------------------------------------------------------
    # Deposit Method
    # ------------------------------------------------------
    def deposit(self, amount):
        if amount <= 0:
            print("Deposit must be positive.")
            return

        self.balance += amount
        self._add_transaction("Deposit", amount)
        print(f"{self.owner} deposited ${amount}")

    # ------------------------------------------------------
    # Withdraw Method
    # ------------------------------------------------------
    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal must be positive.")
            return

        if amount > self.balance:
            print("Insufficient balance!")
            return

        self.balance -= amount
        self._add_transaction("Withdraw", -amount)
        print(f"{self.owner} withdrew ${amount}")

    # ------------------------------------------------------
    # Get Balance
    # ------------------------------------------------------
    def get_balance(self):
        return self.balance

    # ------------------------------------------------------
    # Print Statement
    # ------------------------------------------------------
    def get_statement(self):
        print(f"\n--- Statement for {self.owner} ---")
        for t in self.transactions:
            print(t)

    # ------------------------------------------------------
    # Transfer Method
    # ------------------------------------------------------
    def transfer(self, amount, other_account):
        """
        Transfers money to another BankAccount object.

        Notice: other_account must be another object
        created from BankAccount or its child class.
        """

        if amount > self.balance:
            print("Transfer failed: insufficient funds.")
            return

        self.balance -= amount
        other_account.balance += amount

        self._add_transaction(f"Transfer to {other_account.owner}", -amount)
        other_account._add_transaction(f"Transfer from {self.owner}", amount)

        print(f"{self.owner} transferred ${amount} to {other_account.owner}")


# ==========================================================
# CHILD CLASS: SavingsAccount
# ==========================================================
# Inheritance means this class gets ALL features
# from BankAccount automatically.
#
# So SavingsAccount has:
# deposit, withdraw, transfer, statement, etc.
#
# It can also:
# - Add new features
# - Modify existing behavior (method overriding)


class SavingsAccount(BankAccount):

    def __init__(self, owner, interest_rate):
        """
        super().__init__(owner)

        super() calls the constructor of the parent class.
        This ensures owner, balance, account_number,
        and transactions are properly initialized.
        """

        super().__init__(owner)
        self.interest_rate = interest_rate

    # ------------------------------------------------------
    # Add Interest
    # ------------------------------------------------------
    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        self._add_transaction("Interest added", interest)
        print(f"Interest of ${interest:.2f} added to {self.owner}")

    # ------------------------------------------------------
    # Method Overriding
    # ------------------------------------------------------
    # We override withdraw() to enforce
    # minimum balance rule of $100
    def withdraw(self, amount):

        if self.balance - amount < 100:
            print("Savings account must maintain minimum $100 balance!")
            return

        # Call parent class withdraw logic
        super().withdraw(amount)


# ==========================================================
# MAIN PROGRAM
# ==========================================================

# Create regular accounts
acc1 = BankAccount("Drip")
acc2 = BankAccount("Rahul")

# Create savings account
savings = SavingsAccount("Ankit", 0.05)


# -------------------------------
# Deposits and Withdrawals
# -------------------------------

acc1.deposit(1000)
acc1.withdraw(200)

acc2.deposit(500)

# -------------------------------
# Transfer Between Accounts
# -------------------------------

acc1.transfer(300, acc2)

# -------------------------------
# Savings Account Features
# -------------------------------

savings.deposit(1000)
savings.add_interest()

# Try to overdraw savings (should fail)
savings.withdraw(950)

# Valid withdrawal
savings.withdraw(200)

# -------------------------------
# Print Statements
# -------------------------------

acc1.get_statement()
acc2.get_statement()
savings.get_statement()
