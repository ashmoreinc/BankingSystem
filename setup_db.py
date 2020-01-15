import os
from time import time
FILE_NAME = "data.db"
FILE_PATH = "Files/Data/"

SETUP_SQL = ["""create table admins
(
    id               integer not null
        constraint admins_pk
            primary key,
    first_name       text    not null,
    last_name        text    not null,
    address_line1    text    not null,
    username         text    not null,
    password_hash    text    not null,
    full_rights      integer not null,
    address_line2    text,
    address_line3    text,
    address_city     text default 'Not set' not null,
    address_postcode text default 'aa1 1aa' not null
);""", """create unique index admins_username_uindex
    on admins (username);""", """create table customers
(
    id               integer
        constraint customers_pk
            primary key autoincrement,
    first_name       text not null,
    last_name        text not null,
    address_line1    text not null,
    address_line2    text,
    address_line3    text,
    address_city     text default 'Not set' not null,
    address_postcode text default 'aa1 1aa' not null
)""", """create table accounts
(
    id              integer
        constraint accounts_pk
            primary key autoincrement,
    customer_id     int not null
        references customers
            on delete cascade,
    account_name    text default 'Current Account' not null,
    account_number  int  default 1 not null,
    balance         int  default 0 not null,
    interest_rate   real default 1.0 not null,
    overdraft_limit int  default 0 not null
);""", """create unique index accounts_account_number_uindex
    on accounts (account_number);"""
]

def move_old_db():
    try:
        # Move old file (if it exists) to the backup folder
        os.replace(FILE_PATH + FILE_NAME, FILE_PATH + "Backup/" + FILE_NAME + str(time()) + ".old" )
    except Exception as e:
        print(f"Could not move file. Reason: {str(e)}")

def setup_tables():
    """Set up the tables of the database"""
    import connection

    conn = connection.Connection(db_filepath=FILE_PATH + FILE_NAME, mode="setup")
    for query in SETUP_SQL:
        stat, reply = conn.query(query)
        if stat: print(f"Successfully ran query: \n{query}")
        else: print(f"Failed to run query\n{query}\nReason: {reply}")

    conn.conn.commit()
    conn.close_connection()


def setup_admins():
    """Set up some default admin accounts"""
    import connection
    import bank
    conn = connection.Connection(db_filepath=FILE_PATH + FILE_NAME)

    conn.create_admin_account('Preston', "Garvery", ['The Castle', '', '', 'Boston', 'MA5 SCH'],
                              'admin1', bank.BankingSystem.hash_password('hunter2'), True)
    conn.create_admin_account('Viktor', "Resnov", ['Saint Petersburg', '', '', 'Russia', 'TH3 W0LF'], 'admin2',
                              bank.BankingSystem.hash_password('password123'), False)

    conn.conn.commit()
    conn.close_connection()


def setup_users():
    import bank

    cids = []

    system = bank.BankingSystem(db_filepath=FILE_PATH + FILE_NAME)
    system.login('admin1', 'hunter2')

    stat, reply, cid = system.create_new_customer('John', 'Smith', ['Birmingham City University', 'Curzon', '', 'Birmingham', 'B4 123'])

    if stat:
        print("Created 1 customer.")
        cids.append(cid)
    else:
        print(f"Failed to create customer. Reason: {reply}")

    stat, reply, cid = system.create_new_customer('Jane', 'Doe', ['Birmingham City University',
                                                                  'Curzon', '', 'Birmingham', 'B4 123'])

    if stat:
        print("Created 1 customer.")
        cids.append(cid)
    else:
        print(f"Failed to create customer. Reason: {reply}")

    stat, reply, cid = system.create_new_customer('Viktor', 'Jacks', ['Birmingham City University',
                                                                      'Curzon', '', 'Birmingham', 'B4 123'])

    if stat:
        print("Created 1 customer.")
        cids.append(cid)
    else:
        print(f"Failed to create customer. Reason: {reply}")

    return cids


def setup_accounts(cid1, cid2, cid3):
    import bank

    system = bank.BankingSystem(db_filepath=FILE_PATH + FILE_NAME)
    system.login('admin1', 'hunter2')

    # Customer 1
    stat, reply, accid = system.create_new_account('Current Account', 1.3, 100000, cid1)
    if stat: print("Created 1 account.")
    else: print(f"Failed to create account. Reason: {reply}")

    stat, reply, accid = system.create_new_account('ISA', 2.5, 0, cid1)
    if stat:print("Created 1 account.")
    else:print(f"Failed to create account. Reason: {reply}")

    stat, reply, accid = system.create_new_account('Savings Account', 1.7, 0, cid1)
    if stat: print("Created 1 account.")
    else: print(f"Failed to create account. Reason: {reply}")

    # Customer 2:
    stat, reply, accid = system.create_new_account('Current Account', 1.3, 10000, cid2)
    if stat: print("Created 1 account.")
    else: print(f"Failed to create account. Reason: {reply}")

    stat, reply, accid = system.create_new_account('ISA', 2.5, 0, cid2)
    if stat: print("Created 1 account.")
    else: print(f"Failed to create account. Reason: {reply}")

    # Customer 3
    stat, reply, accid = system.create_new_account('Current Account', 1.3, 0, cid3)
    if stat: print("Created 1 account.")
    else: print(f"Failed to create account. Reason: {reply}")


if __name__ == "__main__":
    print("Moving original DB.")
    move_old_db()
    print("Completed.\n")

    print("Setting up new database tables.")
    setup_tables()
    print("Completed.\n")

    print("Setting up default admin accounts.")
    setup_admins()
    print("Completed.\n")

    print("Setting up default users.")
    cids = setup_users()
    print("Completed.\n")

    print("Setting up accounts.")
    setup_accounts(cids[0], cids[1], cids[2])
    print("Completed.\n")

