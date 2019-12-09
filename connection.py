import sqlite3
from accounts import Customer, BankAccount, Admin


class Connection:
    def __init__(self, db_filepath="Files/Data/data.db"):
        self.connected = False

        try:
            self.conn = sqlite3.connect(db_filepath)
            self.cursor = self.conn.cursor()
            self.connected = True
        except:
            print("Cannot connect to database.")
            self.connected = False

    def close_connection(self):
        """Close connection"""
        try:
            self.conn.close()
        except:
            # Do nothing, cause connection should already be closed if this happens
            pass

        self.connected = False

    def __query(self, query: str) -> bool:
        """Query the data base and return the data"""
        if not self.connected:
            print("Not connected to database.")
            return False

        try:
            self.cursor.execute(query)
            return True
        except Exception as e:
            print(str(e))
            print("An error occurred when querying the database.")
            return False

    def get_customers(self, cid=None, fname=None, lname=None, address=None,
                      must_include_all: bool = False, return_as_dict: bool = False) -> list:
        """Return a list of customers from the database where all provided values are found"""
        if cid is None and fname is None and lname is None and address is None:
            return []
        else:
            sql = "SELECT id, first_name, last_name, address FROM customers WHERE "

            if must_include_all:
                op = 'AND'
            else:
                op = 'OR'

            if cid is not None:
                sql += "id=" + str(cid) + " " + op +" "

            if fname is not None:
                sql += "first_name='" + str(fname) + "' " + op + " "

            if lname is not None:
                sql += "last_name='" + str(lname) + "' " + op + " "

            if address is not None:
                sql += "address='" + str(address) + "' " + op + " "

            # Remove last 4 letters to remove the added operation (op) and two spaces
            sql = sql[:-(len(op) + 2)]

            if self.__query(sql):
                # Get results and convert into a dictionary

                results = []
                for row in self.cursor.fetchall():

                    if return_as_dict:
                        results.append(d)
                        d = {'id': row[0], 'first_name': row[1], 'last_name': row[2], 'address': row[3]}
                    else:
                        cust = Customer(row[0], row[1], row[2], row[3])
                        results.append(cust)

                return results
            else:
                return []

    def get_accounts(self, accid=None, account_name=None, account_number=None, cust_id=None,
                     balance=None, interest_rate=None, overdraft_limit=None,
                     must_include_all: bool = False, return_as_dict: bool = False) -> list:
        """Return a list of accounts from the database where all provided values are found"""
        if accid is None and account_name is None and balance is None and interest_rate is None \
                and overdraft_limit is None and cust_id is None:
            return []
        else:
            sql = "SELECT id, account_name, " \
                  "account_number, balance, interest_rate, overdraft_limit, customer_id FROM accounts WHERE "

            if must_include_all:
                op = 'AND'
            else:
                op = 'OR'

            if accid is not None:
                sql += "id=" + str(accid) + " " + op + " "

            if account_name is not None:
                sql += "account_name='" + str(account_name) + "' " + op + " "

            if account_number is not None:
                sql += "account_number=" + str(account_number) + " " + op + " "

            if balance is not None:
                sql += "balance=" + str(balance) + " " + op + " "

            if interest_rate is not None:
                sql += "interest_rate=" + str(interest_rate) + " " + op + " "

            if overdraft_limit is not None:
                sql += "overdraft_limit=" + str(overdraft_limit) + " " + op + " "

            if cust_id is not None:
                sql += "customer_id=" + str(cust_id) + " " + op + " "

            # remove the operator (op) and two space from the end
            sql = sql[:-(len(op) + 2)]

            if self.__query(sql):
                # Get results and convert into a dictionary
                results = []
                for row in self.cursor.fetchall():
                    d = {'id': row[0], 'account_name': row[1], 'account_number': row[2], 'balance': row[3],
                         'interest_rate': row[4], 'overdraft_limit': row[5], 'customer_id': row[6]}
                    results.append(d)

                if not return_as_dict:
                    class_results = []
                    for res in results:
                        custs = self.get_customers(cid=res["customer_id"])
                        if len(custs) != 1:
                            print(f'Found account id:{res["id"]}, though it is connected to {len(custs)} customers.')
                        else:
                            acc = BankAccount(res["id"], res["account_name"], res["balance"],
                                              res["interest_rate"], res["overdraft_limit"],
                                              res["account_number"], custs[0])
                            class_results.append(acc)
                    return class_results
                return results
            else:
                return []

    def get_admin(self, ad_id: int = None, first_name: str = None, last_name: str = None, address: str = None,
                  username: str = None, full_rights: bool = None,
                  must_include_all: bool = False, return_as_dict: bool = False) -> list:
        """Fetch admin accounts from database"""
        if ad_id is None and first_name is None and last_name is None and address is None \
                and username is None and full_rights is None:
            print("Nothing set.")
            return []
        else:
            sql = "SELECT id, first_name, last_name, address, username, password_hash, full_rights FROM admins WHERE "

            if must_include_all:
                op = "AND"
            else:
                op = "OR"

            if ad_id is not None:
                sql += "id=" + str(ad_id) + " " + op + " "

            if first_name is not None:
                sql += "first_name='" + first_name + "'" + op + " "

            if last_name is not None:
                sql += "last_name='" + last_name + "' " + op + " "

            if address is not None:
                sql += "address='" + address + "' " + op + " "

            if username is not None:
                sql += "username='" + username + "' " + op + " "

            if full_rights is not None:
                sql += "full_rights=" + str(full_rights) + " " + op + " "

            # Remove the operator and 2 spaces from the end
            sql = sql[:-(len(op) + 2)]

            if self.__query(sql):
                # Get results and convert them into the correct form
                results = []
                for row in self.cursor.fetchall():
                    if return_as_dict:
                        # row index order: id, first_name, last_name, address, username, password_hash, full_rights
                        d = {"admin_id": row[0], "first_name": row[1], "last_name": row[2],
                             "address": row[3], "username": row[4], "password_hash": row[5],
                             "full_rights": bool(row[6])}
                        results.append(d)
                    else:
                        admin = Admin(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                        results.append(admin)
                return results
            else:
                print("Query issue")
                return []

    def create_account(self, account_name: str, account_number: int, interest_rate: float, overdraft_limit: int,
                       customer_id: int):
        """Create a new account"""
        sql = f"INSERT INTO accounts (account_name, account_number, balance, interest_rate, overdraft_limit) " \
              f"VALUES ('{account_name}', {account_number}, 0, {interest_rate}, {overdraft_limit})"

        return self.__query(sql)

    def create_admin_account(self, fname: str, lname: str, addr: str,
                             username: str, pass_hash: str, full_rights: int) -> bool:
        """add an admin account"""
        sql = f"INSERT INTO admins (first_name, last_name, address, username, password_hash, full_rights)" \
              f"VALUES ('{fname}', '{lname}', '{addr}', '{username}', '{pass_hash}', '{full_rights}')"

        res = self.__query(sql)
        self.conn.commit()
        return res


if __name__ == "__main__":
    # Testing customer lookup and account retrieval
    print("Testing data retrieval.")
    c = Connection()

    customers = c.get_customers(fname="Cain", must_include_all=True)
    for cust in customers:
        print(cust.get_first_name(), cust.get_last_name())
        accounts = c.get_accounts(cust_id=cust.get_customer_id())
        for account in accounts:
            print("\t" + account.account_name + ": £" + str(account.balance/100))
