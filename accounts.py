class User:
    """User base class"""
    def __init__(self, first_name: str, last_name: str, address: str):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address

    def set_first_name(self, name):
        """Update the users first name"""
        self.first_name = name

    def set_last_name(self, name):
        """Update the users last name"""
        self.last_name = name

    def set_address(self, addr):
        """Update the users address"""
        self.address = addr

    def get_first_name(self):
        """Return the first name of the user"""
        return self.first_name

    def get_last_name(self):
        """Return the last name of the user"""
        return self.last_name

    def get_address(self):
        """Return the address of the user"""
        return self.address


class Customer(User):
    """Stores customer data and functionality"""
    def __init__(self, cid, first_name, last_name, address):
        super(User, self).__init__(first_name, last_name, address)

        # Customer Id (primary key)
        self.customer_id = cid

    def get_customer_id(self):
        """Return the customer id"""
        return self.customer_id


class BankAccount:
    """Bank account"""
    def __init__(self, acc_id: int, account_name: str,
                 balance: int, interest_rate: float, overdraft_limit: int,
                 account_num: int, customer: Customer):
        # Account id (primary key)
        self.account_id = acc_id

        # Balance data
        self.balance = balance
        self.interest_rate = interest_rate
        self.overdraft_limit = overdraft_limit  # The amount the balance is allowed to go below 0

        # Reference to a customer class
        self.customer = customer

        # Account details
        self.account_name = account_name
        self.account_num = account_num

    def get_balance(self):
        """Returns the accounts balance"""
        return self.balance

    def withdraw(self, amount) -> bool:
        """Attempts to remove money from the account if this does not exceed the overdraft limit"""

        # Check if the change will affect the overdraft limit
        if self.balance - amount >= self.balance - self.overdraft_limit:
            self.balance -= amount
            return True
        else:
            return False

    def deposit(self, amount):
        """Increase the balance of the account"""
        self.balance += amount

    def get_account_num(self):
        """Returns the account number"""
        return self.account_num


class Admin(User):
    """Administrator account and controls"""
    def __init__(self, ad_id: int, first_name: str, last_name: str, address: str,
                 username: str, password: str, full_rights: bool):
        super(User, self).__init__(first_name, last_name, address)

        # Set the id, (primary key)
        self.admin_id = ad_id

        # Login details
        self.username = username
        self.password = password

        # Privileges
        self.full_rights = full_rights

    def set_username(self, username):
        """Update the admins username"""
        self.username = username

    def set_password(self, password):
        """Update the admins password"""
        self.password = password

    def get_username(self):
        """Returns the admins username"""
        return self.username

    def get_password(self):
        """Returns the admins password"""
        return self.password

    def set_admin_rights(self, rights: bool):
        """Changes the admins full-rights"""
        self.full_rights = rights

    def has_full_rights(self):
        """Returns the admins full rights status"""
        return self.full_rights


if __name__ == "__main__":
    print("Only to be used as a module.")
    exit()
