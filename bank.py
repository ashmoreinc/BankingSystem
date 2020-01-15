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
    def __init__(self, db_filepath="Files/Data/data.db"):
        self.connection = Connection(db_filepath=db_filepath)

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
    def generate_new_account_number(self) -> int:
        """Generates a randomised account number until a unique one has be found"""
        account_num = None
        unique_num_found = False
        while not unique_num_found:
            # Generate a new, 16 digit number for the account number
            account_num = randint(1000000000000000, 9999999999999999)

            # Check if number is used
            accs, reply = self.connection.get_accounts(account_number=account_num)
            if len(accs) == 0:
                unique_num_found = True

        return account_num

    @require_login
    def create_new_account(self, account_name: str, interest_rate: float,
                           overdraft_limit: int, customer_id: int, account_num: int = None):
        """Create a new account and generate a new, unused account number"""
        if account_num is None:
            account_num = self.generate_new_account_number()

        return self.connection.create_account(account_name, account_num, interest_rate, overdraft_limit, customer_id)

    @require_login
    def create_new_customer(self, fname: str, lname: str, addr: list):
        """Create a new customer"""
        return self.connection.create_customer(fname, lname, addr)

    @require_login
    def update_account(self, accid, **kwargs):
        """Update the account data with the given data"""
        return self.connection.update_account(accid, **kwargs)

    @require_login
    def update_customer(self, cid, **kwargs):
        """Updates the customers data with the given info"""
        return self.connection.update_customer(cid, **kwargs)

    @require_login
    def update_admin(self, adid, **kwargs):
        """Update the admin account"""
        return self.connection.update_admin(adid, **kwargs)

    @require_login
    def update_admin_password(self, old, new, new_conf):
        """Validates passwords then stores them"""

        if new != new_conf:
            return False, "New passwords dont match."

        if not self.verify_hash(self.admin.password, old):
            return False, "Invalid password provided."

        new_hash = self.hash_password(new)

        return self.connection.update_admin_password(self.admin.admin_id, new_hash)

    @require_login
    def delete_account(self, accid):
        """Delete an account from the system with the given id."""
        return self.connection.delete_account(accid)

    @require_login
    def delete_customer(self, cid):
        """remove the customer entry from the database via the connection handler"""

        # Cascade, delete all the accounts connected to the
        data = self.get_customer_data(customer_id=cid)

        accounts = data["accounts"]

        for account in accounts:
            self.delete_account(account.account_id)

        # Now delete the customer
        return self.connection.delete_customer(cid)

    @require_login
    def withdraw(self, acc_id: int, amount: int):
        """Withdraw money from an account"""

        balance, reply = self.connection.get_balance(account_id=acc_id)
        overdraft, reply = self.connection.get_overdraft(account_id=acc_id)

        new_bal = balance - amount

        if new_bal < 0 - overdraft:
            return False, "Insufficient funds available"
        else:
            return self.connection.change_balance(new_bal, account_id=acc_id)

    @require_login
    def deposit(self, acc_id: int, amount: int):
        """Add money to the account"""

        balance, reply = self.connection.get_balance(account_id=acc_id)

        new_bal = balance + amount

        return self.connection.change_balance(new_bal, account_id=acc_id)

    @require_login
    def transfer(self, from_acc_num: int, to_acc_num: int, amount: int) -> tuple:
        """Transfer money from one account to another"""
        # Get the account for the from account
        accounts, reply = self.search_accounts(account_number=from_acc_num)

        if len(accounts) > 0:
            from_acc = accounts[0]
        else:
            return False, "Could not find from account"

        # Get the account for the to account
        accounts, reply = self.search_accounts(account_number=to_acc_num)

        if len(accounts) > 0:
            to_acc = accounts[0]
        else:
            return False, "Could not find to account"
        stat, reason = self.withdraw(from_acc.account_id, amount)
        if stat:
            self.deposit(to_acc.account_id, amount)
            return True, ""
        else:
            return False, f"Could not remove the money from the sender. Reason: {reason}"

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
    def search_customers(self, cid=None, fname=None, lname=None, addr=None,
                         must_include_all=False, exact=True, get_all=False):
        """Issue a search the for customers"""
        if get_all:
            return self.connection.get_customers(get_all=True)
        return self.connection.get_customers(cid=cid, fname=fname, lname=lname,
                                             address_l1=addr[0], address_l2=addr[1], address_l3=addr[2],
                                             address_city=addr[3], address_postcode=addr[4],
                                             must_include_all=must_include_all, exact=exact, get_all=get_all)

    @require_login
    def search_accounts(self, cust_first=None, cust_last=None, get_all=False, **kwargs):
        """Search through the accounts which satisfy the given parameters"""
        if get_all:
            return self.connection.get_accounts(get_all=True)

        accounts_return = []

        if 'exact_fields' in kwargs:
            exact_fields = kwargs['exact_fields']
        else:
            exact_fields = False

        if 'must_include_all' in kwargs:
            include_all = kwargs['must_include_all']
        else:
            include_all = False

        # Check if customer is a search term
        if cust_first is not None:
            if cust_last is not None:
                customers, reply = self.connection.get_customers(fname=cust_first, lname=cust_last,
                                                                 exact=exact_fields, must_include_all=include_all)
            else:
                customers, reply = self.connection.get_customers(fname=cust_first,
                                                                 exact=exact_fields, must_include_all=include_all)
        elif cust_last is not None:
            customers, reply = self.connection.get_customers(lname=cust_last,
                                                             exact=exact_fields, must_include_all=include_all)
        else:
            customers = None

        # Search for all the accounts that all the found customers have
        if customers is not None:
            for customer in customers:
                data = self.get_customer_data(customer.customer_id)

                for new_account in data["accounts"]:
                    # Dont add an account if it is already in the list
                    add_account = True
                    for old_account in accounts_return:
                        if new_account.account_id == old_account.account_id:
                            add_account = False
                            break

                    if add_account:
                        accounts_return.append(new_account)

        # remove the customer data from the kwargs
        if 'cust_first' in kwargs:
            del(kwargs['cust_first'])
        if 'cust_last' in kwargs:
            del(kwargs['cust_last'])

        other_accounts, reply = self.connection.get_accounts(**kwargs)

        # Filter out any already stored accounts
        for new_account in other_accounts:
            add_account = True
            for old_account in accounts_return:
                if new_account.account_id == old_account.account_id:
                    add_account = False
                    break
            if add_account:
                accounts_return.append(new_account)

        return accounts_return, reply

    # Reports
    @require_login
    def interest_report(self) -> dict:
        """Check the interest of all accounts"""
        accounts, reply = self.search_accounts(get_all=True)

        highest_interest = accounts[0]
        lowest_interest = accounts[0]

        cumulative_interest = 0.0

        interest_gained = 0.0

        for account in accounts:
            # Check if highest interest
            if account.interest_rate > highest_interest.interest_rate:
                highest_interest = account

            # Check lowest
            if account.interest_rate < lowest_interest.interest_rate:
                lowest_interest = account

            cumulative_interest += account.interest_rate

            interest_earned = account.calculate_interest_for_year()

            interest_gained += interest_earned

        mean_interest = cumulative_interest / len(accounts)

        data = {"highest": highest_interest,
                "lowest": lowest_interest,
                "mean": mean_interest,
                "interest_gained": interest_gained,
                "accounts_pop": len(accounts)}

        return data

    @require_login
    def overdraft_report(self) -> dict:
        """Calculate the amount of overdrafts given"""
        accounts, reply = self.search_accounts(get_all=True)

        overdraft_total = 0

        overdraft_highest = accounts[0]
        overdraft_lowest = accounts[0]

        for account in accounts:
            # Check highest
            if account.overdraft_limit > overdraft_highest.overdraft_limit:
                overdraft_highest = account

            # Check lowest
            if account.overdraft_limit < overdraft_lowest.overdraft_limit:
                overdraft_lowest = account

            overdraft_total += account.overdraft_limit

        overdraft_mean = overdraft_total / len(accounts)

        data = {"highest": overdraft_highest,
                "lowest": overdraft_lowest,
                "mean": overdraft_mean,
                "total": overdraft_total,
                "accounts_pop": len(accounts)}

        return data

    @require_login
    def balance_report(self) -> dict:
        """Balance report across all accounts"""
        accounts, reply = self.search_accounts(get_all=True)

        max_balance = accounts[0]
        min_balance = accounts[0]

        total_balance = 0.0

        for account in accounts:
            # Highest account balance
            if account.balance > max_balance.balance:
                max_balance = account

            # lowest account balance
            if account.balance < min_balance.balance:
                min_balance = account

            total_balance += account.balance

        mean_balance = total_balance / len(accounts)

        data = {"highest": max_balance,
                "lowest": min_balance,
                "mean": mean_balance,
                "total": total_balance,
                "accounts_pop": len(accounts)}

        return data

    @require_login
    def customer_report(self) -> dict:
        """Creates a report on customers"""
        customers, reply = self.search_customers(get_all=True)

        return {"customers_pop": len(customers)}

if __name__ == "__main__":
    print("Module Only")
    exit()