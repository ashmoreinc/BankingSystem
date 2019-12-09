from accounts import Customer, Admin, BankAccount
from connection import Connection

from random import randint


class BankingSystem:
    """Class that handles the banking system"""
    def __init__(self):
        self.connection = Connection()

        self.logged_in = False
        self.admin = None

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

    def create_admin(self, fname, lname, addr, username, password, full_rights):
        """Create a new admin account with the given details"""

        # Only admins with full rights can create a new admin
        # Return false if not, or if not logged in
        if self.logged_in:
            if not self.admin.has_full_rights():
                print("Rights issues")
                return False
        else:
            print("Log in issues")
            return False

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

    def login(self, username, password) -> bool:
        """verify login details and then set the admin"""

        if not self.connection.connected:
            print("Connection issue.")
            return False

        # Fetch the admin class
        admin = self.connection.get_admin(username=username)  # Returns the admin class
        if len(admin) != 1:
            print(f"Users found: {len(admin)}")
            return False
        else:
            admin = admin[0]  # Turn list into single element

        if self.verify_hash(admin.get_password(), password):
            self.admin = admin
            self.logged_in = True
            return True
        else:
            print("Could not verify hash.")
            return False

    def log_out(self):
        """Changes log in status and connected admin"""
        self.admin = None
        self.logged_in = False


if __name__ == "__main__":
    sys = BankingSystem()

    stat = sys.login('ashmoreinc', 'hunter2')
