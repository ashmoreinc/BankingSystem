from accounts import Customer, Admin, BankAccount
from connection import Connection

from random import randint


# Decorators
def require_login(function):
    # Only allows the function to run if the logged_in attr is True
    def wrapper(self, *args, **kwargs):
        if self.logged_in:
            return function(self, *args, **kwargs)
        return "Admin log-on required."
    return wrapper


def require_full_rights(function):
    # Only allows the function to run if the logged_in attr is true and the admin attr has full rights
    def wrapper(self, *args, **kwargs):
        if self.logged_in:
            if self.admin.has_full_rights():
                return function(self, *args, **kwargs)
            else:
                return "Admin must have full access rights."
        else:
            return "Admin log-on required."
    return wrapper


class BankingSystem:
    """Class that handles the banking system"""
    def __init__(self):
        self.connection = Connection()

        self.logged_in = False
        self.admin = None

    # Hashing systems
    # adapted from https://www.vitoshacademy.com/hashing-passwords-in-python/
    @staticmethod
    def hash_password(password):
        """Hash&salt a string"""
        import hashlib, binascii, os
        # Generate random salt
        salt = hashlib.sha3_512(os.urandom(60)).hexdigest().encode('ascii')

        # Hash password and salt
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt, 100000)

        pwdhash = binascii.hexlify(pwdhash)
        # Return hash
        return (salt + pwdhash).decode('ascii')

    @staticmethod
    def verify_hash(stored_hash, password):
        """Hash the password and compared with the stored data"""
        import hashlib
        import binascii
        # Separate the salt and hash
        salt = stored_hash[:128]
        stored_hash = stored_hash[128:]

        # Hash the provided password
        passhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        passhash = binascii.hexlify(passhash).decode('ascii')

        return stored_hash == passhash

    # Admin and login control
    @require_full_rights
    def create_admin(self, fname, lname, addr, username, password, full_rights):
        """Create a new admin account with the given details"""

        # Return false if there's no db connection
        if not self.connection.connected:
            print("Database connection issue.")
            return False

        # Return false if username is already taken
        accs = self.connection.get_admin(username=username)

        if len(accs) > 0:
            print("To many users!")
            return False

        # Hash the password
        hash_res = self.hash_password(password)

        if full_rights:
            rights = 1
        else:
            rights = 0

        return self.connection.create_admin_account(fname, lname, addr, username, hash_res, rights)

    def login(self, username, password) -> tuple:
        """verify login details and then set the admin"""

        if not self.connection.connected:
            return False, "Connection to database could not be established."

        # Fetch the admin class
        admin, reply = self.connection.get_admin(username=username)  # Returns the admin class
        if len(admin) > 1:
            return False, "Bad information received from the database."
        elif len(admin) < 1:
            return False, "Login credentials are invalid."
        else:
            admin = admin[0]  # Turn list into single element

        if self.verify_hash(admin.get_password(), password):
            self.admin = admin
            self.logged_in = True
            return True, ""
        else:
            return False, "Login credentials are invalid."

    def log_out(self):
        """Changes log in status and connected admin"""
        self.admin = None
        self.logged_in = False

    # Account and customer control
    @require_login
    def create_new_account(self, account_name: str, interest_rate: float,
                           overdraft_limit: int, customer_id: int):
        """Create a new account and generate a new, unused account number"""
        account_num = None
        unique_num_found = False
        while not unique_num_found:
            # Generate a new, 16 digit number for the account number
            account_num = randint(1000000000000000, 9999999999999999)

            # Check if number is used
            accs = self.connection.get_accounts(account_number=account_num)
            if len(accs) == 0:
                unique_num_found = True

        return self.connection.create_account(account_name, account_num, interest_rate, overdraft_limit, customer_id)

    @require_login
    def creat_new_customer(self, fname: str, lname: str, addr: list):
        """Create a new customer"""
        return self.connection.create_customer(fname, lname, addr)

    @require_login
    def withdraw(self, acc_id: int, amount: int):
        """Withdraw money from an account"""

        balance = self.connection.get_balance(account_id=acc_id)
        overdraft = self.connection.get_overdraft(account_id=acc_id)

        new_bal = balance - amount

        if new_bal < 0 - overdraft:
            return False
        else:
            return self.connection.change_balance(new_bal, account_id=acc_id)

    @require_login
    def deposit(self, acc_id: int, amount: int):
        """Add money to the account"""

        balance = self.connection.get_balance(account_id=acc_id)

        new_bal = balance + amount

        return self.connection.change_balance(new_bal, account_id=acc_id)

    @require_login
    def get_customer_data(self, customer_id: int) -> dict:
        """Gets all customer data including connected accounts"""
        # As the customer id field is unique, there should only be one item available in the list stored as data
        data, reply = self.connection.get_customers(cid=customer_id)

        # data is a list of customer classes, check there is any customers
        # if their isn't, return None in place of the data
        if len(data) < 1:
            return {'customer': None, 'accounts': None}

        customer = data[0]

        # Get all the connected accounts
        accounts, reply = self.connection.get_accounts(cust_id=customer_id)

        return_data = {'customer': customer, 'accounts': accounts}
        return return_data

    @require_login
    def get_account_data(self, account_id: int) -> BankAccount:
        """Gets the account information and returns the BankAccount object.
        Don't return customer as the customer is store in the class"""
        # As the account has a unique id, only one element should be returned when selecting via id
        data, reply = self.connection.get_accounts(accid=account_id)

        # Data is a list of Account classes, check if there is only 1
        if len(data) != 1:
            return None

        account = data[0]

        return account

    @require_login
    def search_customers(self, cid=None, fname=None, lname=None, addr=None, must_include_all=False, exact=True):
        """Issue a search the for customers"""
        return self.connection.get_customers(cid=cid, fname=fname, lname=lname,
                                             address_l1=addr[0], address_l2=addr[1], address_l3=addr[2],
                                             address_city=addr[3], address_postcode=addr[4],
                                             must_include_all=must_include_all, exact=exact)

if __name__ == "__main__":
    sys = BankingSystem()
    # Test log in
    # Test full rights account
    sys.login('ashmoreinc', 'hunter2')
