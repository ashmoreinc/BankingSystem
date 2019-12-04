import sqlite3


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

    def get_customers(self, cid=None, fname=None, lname=None, address=None):
        """Return a list of customers from the database where all provided values are found"""
        if cid is None and fname is None and lname is None and address is None:
            return []
        else:
            sql = "SELECT id, first_name, last_name, address FROM customers WHERE "

            if cid is not None:
                sql += "cid=" + str(cid) + " OR "

            if fname is not None:
                sql += "first_name='" + str(fname) + "' OR "

            if lname is not None:
                sql += "last_name='" + str(lname) + "' OR "

            if address is not None:
                sql += "address='" + str(address) + "' OR "

            # Remove last 4 letters to remove the added ' OR '
            sql = sql[:-4]

            if self.__query(sql):
                # Get results and convert into a dictionary
                results = []
                for row in self.cursor.fetchall():
                    d = {'id': row[0], 'first_name': row[1], 'last_name': row[2], 'address': row[3]}
                    results.append(d)
                return results
            else:
                return []

    def get_accounts(self, accid=None, account_name=None,
                     balance=None, interest_rate=None, overdraft_limit=None,
                     cust_id=None):
        """Return a list of accounts from the database where all provided values are found"""
        if accid is None and account_name is None and balance is None and interest_rate is None \
                and overdraft_limit is None and cust_id is None:
            return []
        else:
            sql = "SELECT id, account_name, " \
                  "account_number, balance, interest_rate, overdraft_limit, customer_id FROM accounts WHERE "

            if accid is not None:
                sql += "id=" + str(accid) + " OR "

            if account_name is not None:
                sql += "account_name='" + str(account_name) + "' OR "

            if balance is not None:
                sql += "balance=" + str(balance) + " OR "

            if interest_rate is not None:
                sql += "interest_rate=" + str(interest_rate) + " OR "

            if overdraft_limit is not None:
                sql += "overdraft_limit=" + str(overdraft_limit) + " OR "

            if cust_id is not None:
                sql += "customer_id=" + str(cust_id) + " OR "

            sql = sql[:-4]

            if self.__query(sql):
                # Get results and convert into a dictionary
                results = []
                for row in self.cursor.fetchall():
                    d = {'id': row[0], 'account_name': row[1], 'account_number': row[2], 'balance': row[3],
                         'interest_rate': row[4], 'overdraft_limit': row[5], 'customer_id': row[6]}
                    results.append(d)
                return results
            else:
                return []


if __name__ == "__main__":
    print("Testing data retrieval.")
    c = Connection()

    out = c.get_accounts(cust_id=1)
    print(out)

    out = c.get_customers(fname="Cain")
    print(out)
