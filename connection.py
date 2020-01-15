import sqlite3
from accounts import Customer, BankAccount, Admin


class Connection:
    def __init__(self, db_filepath="Files/Data/data.db", mode="normal"):
        self.connected = False

        # To limit functions to setup mode
        self.mode = mode

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

    def __query(self, query: str):
        """Query the data base and return the data"""
        if not self.connected:
            return False, "Not connected to database."

        try:
            self.cursor.execute(query)
            return True, "Successfully executed query"
        except Exception as e:
            print(str(e))
            return False, "An error occurred when querying the database."

    def query(self, query: str):
        """Runs the __query but helps for setup"""

        if self.mode == "setup":
            return self.__query(query)
        else:
            print("Can only run query() in setup mode.")

    # Getters

    def get_customers(self, cid=None, fname=None, lname=None,
                      address_l1=None, address_l2=None, address_l3=None, address_city=None, address_postcode=None,
                      must_include_all: bool = False, exact: bool = True,
                      return_as_dict: bool = False, get_all: bool = False) -> tuple:
        """Return a list of customers from the database where all provided values are found"""
        if (cid is None and fname is None and lname is None and
                address_l1 is None and address_l2 is None and address_l3 is None and
                address_city is None and address_postcode is None) and not get_all:
            return [], "No search data provided."
        else:
            if get_all:
                sql = "SELECT id, first_name, last_name, " \
                      "address_line1, address_line2, address_line3, address_city, address_postcode " \
                      "FROM customers"
            else:
                sql = "SELECT id, first_name, last_name, " \
                      "address_line1, address_line2, address_line3, address_city, address_postcode FROM customers WHERE "

                if must_include_all:
                    op = 'AND'
                else:
                    op = 'OR'

                if cid is not None:
                    # Exact will not affect cid as it is unique
                    sql += f"id={str(cid)} {op} "

                if fname is not None:
                    if exact:
                        sql += f"first_name='{str(fname)}' {op} "
                    else:
                        sql += f"first_name LIKE '%{str(fname)}%' {op} "

                if lname is not None:
                    if exact:
                        sql += f"last_name='{str(lname)}' {op} "
                    else:
                        sql += f"last_name LIKE '%{str(lname)}%' {op} "

                if address_l1 is not None:
                    if exact:
                        sql += f"address_line1='{str(address_l1)}' {op} "
                    else:
                        sql += f"address_line1 LIKE '%{str(address_l1)}%' {op} "

                if address_l2 is not None:
                    if exact:
                        sql += f"address_line2='{str(address_l2)}' {op} "
                    else:
                        sql += f"address_line2 LIKE '%{str(address_l2)}%' {op} "

                if address_l3 is not None:
                    if exact:
                        sql += f"address_line3='{str(address_l3)}' {op} "
                    else:
                        sql += f"address_line3 LIKE '%{str(address_l3)}%' {op} "

                if address_city is not None:
                    if exact:
                        sql += f"address_city='{str(address_city)}' {op} "
                    else:
                        sql += f"address_city LIKE '%{str(address_city)}%' {op} "

                if address_postcode is not None:
                    if exact:
                        sql += f"address_postcode='{str(address_postcode)}' {op} "
                    else:
                        sql += f"address_postcode LIKE '%{str(address_postcode)}%' {op} "

                # Remove last 4 letters to remove the added operation (op) and two spaces
                sql = sql[:-(len(op) + 2)]

            query_status, query_reply = self.__query(sql)

            if query_status:
                # Get results and convert into a dictionary

                results = []
                for row in self.cursor.fetchall():

                    if return_as_dict:
                        d = {'id': row[0], 'first_name': row[1], 'last_name': row[2],
                             'address': [row[3], row[4], row[5], row[6], row[7]]}
                        results.append(d)
                    else:
                        cust = Customer(row[0], row[1], row[2], [row[3], row[4], row[5], row[6], row[7]])
                        results.append(cust)

                return results, f"Query ran successfully. {len(results)} entries found."
            else:
                return [], query_reply

    def get_accounts(self, accid=None, account_name=None, account_number=None, cust_id=None,
                     balance=None, balance_opts='=', interest_rate=None, interest_opts='=',
                     overdraft_limit=None, overdraft_opts='=',
                     must_include_all: bool = False, exact_fields=False, return_as_dict: bool = False, get_all: bool = False) -> tuple:
        """Return a list of accounts from the database where all provided values are found"""
        if (accid is None and account_name is None and account_number is None and
                balance is None and interest_rate is None and overdraft_limit is None and cust_id is None) \
                and not get_all:
            return [], "No search data provided."
        else:
            if get_all:
                sql = "SELECT id, account_name, " \
                      "account_number, balance, interest_rate, overdraft_limit, customer_id FROM accounts"
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
                    if exact_fields:
                        sql += "account_name='" + str(account_name) + "' " + op + " "
                    else:
                        sql += "account_name LIKE'%" + str(account_name) + "%' " + op + " "

                if account_number is not None:
                    sql += "account_number=" + str(account_number) + " " + op + " "

                if balance is not None:
                    if balance_opts == ">":
                        sql += "balance>=" + str(balance) + " " + op + " "
                    elif balance_opts == "<":
                        sql += "balance<=" + str(balance) + " " + op + " "
                    else:
                        sql += "balance=" + str(balance) + " " + op + " "

                if interest_rate is not None:
                    if interest_opts == ">":
                        sql += "interest_rate>=" + str(interest_rate) + " " + op + " "
                    elif interest_opts == "<":
                        sql += "interest_rate<=" + str(interest_rate) + " " + op + " "
                    else:
                        sql += "interest_rate=" + str(interest_rate) + " " + op + " "

                if overdraft_limit is not None:
                    if overdraft_opts == ">":
                        sql += "overdraft_limit>=" + str(overdraft_limit) + " " + op + " "
                    elif overdraft_opts == "<":
                        sql += "overdraft_limit<=" + str(overdraft_limit) + " " + op + " "
                    else:
                        sql += "overdraft_limit=" + str(overdraft_limit) + " " + op + " "

                if cust_id is not None:
                    sql += "customer_id=" + str(cust_id) + " " + op + " "

                # remove the operator (op) and two space from the end
                sql = sql[:-(len(op) + 2)]

            query_status, query_reply = self.__query(sql)

            if query_status:
                # Get results and convert into a dictionary
                results = []
                for row in self.cursor.fetchall():
                    d = {'id': row[0], 'account_name': row[1], 'account_number': row[2], 'balance': row[3],
                         'interest_rate': row[4], 'overdraft_limit': row[5], 'customer_id': row[6]}
                    results.append(d)

                if not return_as_dict:
                    class_results = []
                    for res in results:
                        custs, reply = self.get_customers(cid=res["customer_id"])
                        if len(custs) != 1:
                            # No customer connected to this account so dont add to the list
                            # print(f'Found account id:{res["id"]}, though it is connected to {len(custs)} customers.')
                            pass
                        else:
                            acc = BankAccount(res["id"], res["account_name"], res["balance"],
                                              res["interest_rate"], res["overdraft_limit"],
                                              res["account_number"], custs[0])
                            class_results.append(acc)
                    return class_results, f"Query ran successfully. {len(class_results)} entries found"
                return results, f"Query ran successfully. {len(results)} entries found"
            else:
                return [], query_reply

    def get_admin(self, ad_id: int = None, first_name: str = None, last_name: str = None,
                  address_l1: str = None, address_l2: str = None, address_l3: str = None,
                  address_city: str = None, address_postcode: str = None,
                  username: str = None, full_rights: bool = None,
                  must_include_all: bool = False, return_as_dict: bool = False) -> tuple:
        """Fetch admin accounts from database"""
        if ad_id is None and first_name is None and last_name is None \
                and address_l1 is None and address_l2 is None and address_l3 is None and \
                address_city is None and address_postcode is None \
                and username is None and full_rights is None:
            return [], "No search data has been provided."
        else:
            sql = "SELECT id, first_name, last_name, address_line1, address_line2, address_line3, address_city, " \
                  "address_postcode, username, password_hash, full_rights FROM admins WHERE "

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

            if address_l1 is not None:
                sql += "address_line1='" + address_l1 + "' " + op + " "

            if address_l2 is not None:
                sql += "address_line2='" + address_l2 + "' " + op + " "

            if address_l3 is not None:
                sql += "address_line3='" + address_l3  + "' " + op + " "

            if address_city is not None:
                sql += "address_city='" + address_city + "' " + op + " "

            if address_postcode is not None:
                sql += "address_postcode='" + address_postcode + "' " + op + " "

            if username is not None:
                sql += "username='" + username + "' " + op + " "

            if full_rights is not None:
                sql += "full_rights=" + str(full_rights) + " " + op + " "

            # Remove the operator and 2 spaces from the end
            sql = sql[:-(len(op) + 2)]

            query_status, query_reply = self.__query(sql)

            if query_status:
                # Get results and convert them into the correct form
                results = []
                for row in self.cursor.fetchall():
                    if return_as_dict:
                        # row index order: id, first_name, last_name, address, username, password_hash, full_rights
                        d = {"admin_id": row[0], "first_name": row[1], "last_name": row[2],
                             "address": [row[3], row[4], row[5], row[6], row[7]],
                             "username": row[8], "password_hash": row[9], "full_rights": bool(row[10])}
                        results.append(d)
                    else:
                        admin = Admin(row[0], row[1], row[2], [row[3], row[4], row[5], row[6], row[7]],
                                      row[8], row[9], row[10])
                        results.append(admin)
                return results, f"Query ran successfully. {len(results)} entries found."
            else:
                return [], query_reply

    def get_balance(self, account_id: int = None, account_number: int = None) -> tuple:
        """Get the balance of an account"""
        if account_id is None and account_number is None:
            return None, "No search data provided."

        sql = "SELECT balance FROM accounts WHERE "

        if account_id is not None:
            sql += f"id={account_id} AND "

        if account_number is not None:
            sql += f"account_number={account_number}"

        if sql[-4:] == "AND ":
            sql = sql[:-4]

        query_status, query_reply = self.__query(sql)

        if query_status:
            ret = self.cursor.fetchall()
            if len(ret) != 1:
                print("Too many entries")
                return None, f"{len(ret)}, entries found."
            else:
                data = ret[0]  # returns the whole row
                return int(data[0]), "Query returned data"  # Just return the first value, which should be balance
        else:
            return None, query_reply

    def get_overdraft(self, account_id: int = None, account_number: int = None) -> tuple:
        """Get the overdraft limit of an account"""
        if account_id is None and account_number is None:
            return None, "No search data provided"

        sql = "SELECT overdraft_limit FROM accounts WHERE "

        if account_id is not None:
            sql += f"id={account_id} AND "

        if account_number is not None:
            sql += f"account_number={account_number}"

        if sql[-4:] == "AND ":
            sql = sql[:-4]

        query_status, query_reply = self.__query(sql)

        if query_status:
            ret = self.cursor.fetchall()
            if len(ret) != 1:
                return None, f"{len(ret)} entries returned."
            else:
                data = ret[0]  # returns the whole row
                return int(data[0]), "Query ran successfully."  # Just return the first value, which should be balance
        else:
            return None, query_reply

    # Update table entries
    def change_balance(self, new_balance: int, account_id: int = None, account_number: int = None) -> tuple:
        """Change the balance data of an account"""
        if account_id is None and account_number is None:
            return False, "No search data provided."

        sql = f"UPDATE accounts " \
              f"SET balance={new_balance} " \
              f"WHERE "

        if account_id is not None:
            sql += f"id={account_id} AND "

        if account_number is not None:
            sql += f"account_number={account_number}"

        if sql[-4:] == "AND ":
            sql = sql[:-4]

        query_status, query_reply = self.__query(sql)

        if query_status:
            self.conn.commit()
            return True, "Updated."
        else:
            return False, query_reply

    def update_customer(self, cid, fname: str = None, lname: str = None, addr: list = None):
        """Update the customer entry"""
        if fname is None and lname is None and addr == [None, None, None, None, None]:
            return False, "No data is set to be updated", None
        else:
            sql = "UPDATE customers " \
                  "SET "

            if fname is not None:
                sql += f"first_name='{str(fname)}', "

            if lname is not None:
                sql += f"last_name='{str(lname)}', "

            if addr[0] is not None:
                sql += f"address_line1='{str(addr[0])}', "

            if addr[1] is not None:
                sql += f"address_line2='{str(addr[1])}', "

            if addr[2] is not None:
                sql += f"address_line3='{str(addr[2])}', "

            if addr[3] is not None:
                sql += f"address_city='{str(addr[3])}', "

            if addr[4] is not None:
                sql += f"address_postcode='{str(addr[4])}', "

            # Remove the comma and space that are at the end.
            sql = sql[:-2]

            sql += f" WHERE id={cid}"

            stat, repl = self.__query(sql)
            if stat:
                self.conn.commit()
                # Get the new customer object
                customer, reply = self.get_customers(cid=cid)
                return True, "Updated.", customer
            else:
                return False, repl, None

    def update_account(self, accid, account_name: str = None, overdraft_limit: int = None,
                       interest_rate: float = None) -> tuple:
        """Update the account details with the given data"""
        if account_name is None and overdraft_limit is None and interest_rate is None:
            return False, "No new data has been provided.", None
        else:
            sql = "UPDATE accounts SET "

            if account_name is not None:
                sql += f"account_name='{account_name}', "

            if overdraft_limit is not None:
                sql += f"overdraft_limit={overdraft_limit}, "

            if interest_rate is not None:
                sql += f"interest_rate={interest_rate}, "

            # Remove the trailing ", " that is present
            sql = sql[:-2]

            # Add the where statement
            sql += f" WHERE id={accid}"

            status, reply = self.__query(sql)

            if status:
                # Get the new account
                # As we are using the id and id is the primary key, there should always be only one account found
                self.conn.commit()
                acc = self.get_accounts(accid=accid)[0][0]

                return status, "Successfully update account info", acc
            else:
                return status, reply, None

    def update_admin(self, adid, first_name: str = None, last_name: str = None, username: str = None,
                     addr_l1: str = None, addr_l2: str = None, addr_l3: str = None,
                     addr_city: str = None, addr_post: str = None,
                     full_rights: int = None, password_hash: str = None) -> tuple:
        """Update the admin account details"""
        if first_name is None and last_name is None and username is None and addr_l1 is None and addr_l2 is None \
                and addr_l3 is None and addr_city is None and addr_post is None and \
                full_rights is None and password_hash is None:
            return False, "No data has been provided.", None
        else:
            sql = "UPDATE admins SET "

            if first_name is not None:
                sql += f"first_name='{first_name}', "

            if last_name is not None:
                sql += f"last_name='{last_name}', "

            if username is not None:
                sql += f"username='{username}', "

            if addr_l1 is not None:
                sql += f"address_line1='{addr_l1}', "

            if addr_l2 is not None:
                sql += f"address_line2='{addr_l2}', "

            if addr_l3 is not None:
                sql += f"address_line3='{addr_l3}', "

            if addr_post is not None:
                sql += f"address_postcode='{addr_post}', "

            if addr_city is not None:
                sql += f"address_city='{addr_city}', "

            if full_rights is not None:
                sql += f"full_rights={full_rights}, "

            if password_hash is not None:
                sql += f"password_hash='{password_hash}', "

            sql = sql[:-2]
            sql += f" WHERE id={adid}"

            status, reply = self.__query(sql)

            if status:
                self.conn.commit()
                # Get the new admin object
                admins, reply = self.get_admin(adid)
                admin = admins[0]

                return True, "Successfully Updated", admin
            else:
                return status, reply, None

    def update_admin_password(self, adid: int, new_hash: str) -> bool:
        """Updates the accounts hash with the new one provided"""
        sql = f"UPDATE admins SET password_hash='{new_hash}' WHERE id={adid}"

        stat, repl = self.__query(sql)

        if stat:
            self.conn.commit()

        return stat, repl

    # Create new table entries
    def create_customer(self, fname: str, lname: str, addr: list) -> tuple:
        """Create a new table entry for the customer"""
        sql = f"INSERT INTO customers " \
              f"(first_name, last_name, address_line1, address_line2, address_line3, address_city, address_postcode)" \
              f"VALUES ('{fname}', '{lname}', '{addr[0]}', '{addr[1]}', '{addr[2]}', '{addr[3]}', '{addr[4]}')"

        stat, repl = self.__query(sql)
        self.conn.commit()
        cid = self.cursor.lastrowid
        return stat, repl, cid

    def create_account(self, account_name: str, account_number: int, interest_rate: float, overdraft_limit: int,
                       customer_id: int) -> tuple:
        """Create a new account"""
        sql = f"INSERT INTO accounts (account_name, account_number, balance, interest_rate, overdraft_limit, customer_id) " \
              f"VALUES ('{account_name}', {account_number}, 0, {interest_rate}, {overdraft_limit}, {customer_id})"

        stat, repl = self.__query(sql)
        self.conn.commit()
        accid = self.cursor.lastrowid
        return stat, repl, accid

    def create_admin_account(self, fname: str, lname: str, addr: list,
                             username: str, pass_hash: str, full_rights: int) -> tuple:
        """add an admin account"""
        sql = f"INSERT INTO admins " \
              f"(first_name, last_name, address_line1, address_line2, address_line3, address_city, address_city, " \
              f"username, password_hash, full_rights)" \
              f"VALUES ('{fname}', '{lname}', '{addr[0]}', '{addr[1]}', '{addr[2]}', '{addr[3]}', '{addr[4]}', " \
              f"'{username}', '{pass_hash}', '{full_rights}')"
        stat, repl = self.__query(sql)
        self.conn.commit()
        adid = self.cursor.lastrowid
        return stat, repl, adid

    # Delete table rows
    def delete_customer(self, cid):
        """Remove the customer row"""

        # We do not need to delete all the connected accounts as they are set to cascade
        sql = f"DELETE FROM customers WHERE id={int(cid)}"

        stat, repl = self.__query(sql)
        if stat:
            self.conn.commit()
        return stat, repl

    def delete_account(self, accid):
        """Remove the account row"""

        sql = f"DELETE FROM accounts WHERE id={int(accid)}"

        stat, repl = self.__query(sql)

        if stat:
            self.conn.commit()

        return stat, repl


if __name__ == "__main__":
    print("Module Only use")
    exit()
