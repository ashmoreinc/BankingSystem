import tkinter as tk
import tkinter.ttk as ttk

import bank

SYSTEM = bank.BankingSystem()

FONTS = {"l": ("Helvetica", 20), "m": ("Helvetica", 16), "s": ("Helvetica", 12)}


class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Bank Management System")

        self.geometry("1280x720")
        # Full Screen Option padx=5
        # self.attributes("-fullscreen", True)

        # Container for each page
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.Pages = {}
        for page in (HomePage, LandingPage, CustomerView, CustomerSearch, CustomerCreate, AccountView):  # Populate with pages
            p = page(container, self)

            self.Pages[page.__name__] = p
            p.grid(row=0, column=0, sticky="nsew")

            p.initialise()
        self.show_page(HomePage.__name__)

    def show_page(self, page_name):
        page = self.Pages[page_name]
        page.page_update()
        page.tkraise()


def create_navigation_bar(parent, window_controller, show_home_button=True):
    """Creates a navigation bar as a child to the given parent"""
    # Page top header
    header_frame = tk.Frame(parent)
    header_frame.pack(side="top", fill="x", pady=2)

    # Home button
    if show_home_button:
        tk.Button(header_frame, text="Home", font=FONTS["m"],
                  command=lambda: window_controller.show_page(LandingPage.__name__)).pack(side="left", fill="y")

    # account button
    tk.Button(header_frame, text="Your Account", font=FONTS["m"]).pack(side="right", fill="y")

    # header separator
    ttk.Separator(parent).pack(side="top", fill="x")


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Create the canvas and scroll bar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)

        # Create the widget that will be parent to all the widgets added
        self.widget_frame = tk.Frame(canvas)

        # Bind the configure event to the canvas configuration of the scroll region
        self.widget_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.widget_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class PageBase(tk.Frame):
    """Basis for the page classes"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

    def initialise(self):
        """To be overriden with tasks that must be completed on class initialisation by the controller class Window"""
        pass

    def page_update(self):
        """To be overriden with tasks that must be completed when this page is switched too"""
    pass


class HomePage(PageBase):
    """First page the users will see"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Text Label
        tk.Label(self, text="Banking Management System", font=FONTS["l"]).pack(side="top", fill="x", pady=5, padx=5)

        ttk.Separator(self).pack(side="top", fill="x", padx=15, pady=5)

        # Log in section

        form_frame = tk.Frame(self)
        form_frame.pack(side="top", pady=15)

        # Username_field
        tk.Label(form_frame, text="Username", font=FONTS["m"]).grid(row=0, column=0, sticky="nsew", pady=5)

        self.username_entry = tk.Entry(form_frame, font=FONTS["m"], width=20)
        self.username_entry.grid(row=0, column=1, sticky="ew")

        # Password field
        tk.Label(form_frame, text="Password", font=FONTS["m"]).grid(row=1, column=0, sticky="nsew", pady=5)

        self.password_entry = tk.Entry(form_frame, show="*", font=FONTS["m"], width=20)
        self.password_entry.grid(row=1, column=1, sticky="ew")

        # Failure text
        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="x", pady=5, padx=5)

        # Enter button
        tk.Button(self, text="Log in.", width=15, font=FONTS["m"], bg="#00dd00",
                  command=self.login).pack(side="top", pady=5, padx=15)

    def login(self):
        """Function ran on login button click"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        status, msg = SYSTEM.login(username, password)

        if status:
            self.controller.show_page(LandingPage.__name__)
        else:
            self.fail_text.configure(text=msg)


class LandingPage(PageBase):
    """The page the user lands at when the log in"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller, show_home_button=False)

        # Everything else will go in here.
        # Split into a separate frame so that we dont have any problems with the pack manager used for self
        content_frame = tk.Frame(self)
        content_frame.pack(side="top", fill="both", expand=True)

        # Reports frame
        reports_frame = tk.Frame(content_frame)
        reports_frame.pack(side="right", fill="y", padx=25)

        # Add a separator between reports and customer
        ttk.Separator(content_frame, orient="vertical").pack(side="right", fill="y")

        # Customer Management Frame
        customer_frame = tk.Frame(content_frame)
        customer_frame.pack(side="left", fill="both", expand=True)

        # Report frame Label
        tk.Label(reports_frame, text="Reports", font=FONTS["l"]).pack(side="top", fill="x", padx=50)

        # TODO: Create Report functionality

        # Customer Control
        cust_manage = tk.Frame(customer_frame)
        cust_manage.pack(side="top", fill="both", expand=True)

        tk.Label(cust_manage, text="Customer Management", font=FONTS["l"]).grid(row=0, column=0, columnspan=2)

        # Buttons
        tk.Button(cust_manage, text="Search", font=FONTS["m"],
                  command=lambda: controller.show_page(CustomerSearch.__name__)).grid(row=1, column=0, sticky="w")

        tk.Button(cust_manage, text="Create", font=FONTS["m"],
                  command=lambda: controller.show_page(CustomerCreate.__name__)).grid(row=1, column=1, sticky="w")

        # Separate customer and account section
        ttk.Separator(customer_frame).pack(side="top", fill="x")

        # Account Control
        account_manage = tk.Frame(customer_frame)
        account_manage.pack(side="top", fill="both", expand=True)

        tk.Label(account_manage, text="Account Management", font=FONTS["l"]).grid(row=0, column=0, columnspan=2)


class CustomerSearch(PageBase):
    """Search function for customers"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Search Customers", font=FONTS["l"]).pack(side="top", fill="x", pady=10)

        # content frame
        content_frame = tk.Frame(self)
        content_frame.pack(side="top", fill="both", expand=True)

        # input frame
        query_frame = tk.Frame(content_frame)
        query_frame.pack(side="left", fill="y", pady=10)

        # Separate Frame
        ttk.Separator(content_frame, orient="vertical").pack(side="left", fill="y", pady=10, padx=10)

        # output/results frame
        results = ScrollableFrame(content_frame)
        results.pack(side="right", fill="both", expand=True)

        self.results_frame = results.widget_frame

        # Create the search input fields
        row = 0  #  Use a row variable so we can quickly add widgets in and swap them easily without hardcoded rows

        # id
        tk.Label(query_frame, text="Customer ID: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.cust_id = tk.Entry(query_frame, font=FONTS["m"])
        self.cust_id.grid(row=row, column=1)

        row += 1

        # first name
        tk.Label(query_frame, text="First Name: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.first_name = tk.Entry(query_frame, font=FONTS["m"])
        self.first_name.grid(row=row, column=1)

        row += 1

        # last name
        tk.Label(query_frame, text="Last Name: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.last_name = tk.Entry(query_frame, font=FONTS["m"])
        self.last_name.grid(row=row, column=1)

        row += 1

        # Separate
        ttk.Separator(query_frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=5, padx=10)

        row += 1

        # addr
        #       Line 1
        tk.Label(query_frame, text="Address Line 1: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.addr1 = tk.Entry(query_frame, font=FONTS["m"])
        self.addr1.grid(row=row, column=1)

        row += 1

        #       Line 2
        tk.Label(query_frame, text="Address Line 2: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.addr2 = tk.Entry(query_frame, font=FONTS["m"])
        self.addr2.grid(row=row, column=1)

        row += 1

        # Line 3
        tk.Label(query_frame, text="Address Line 3: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.addr3 = tk.Entry(query_frame, font=FONTS["m"])
        self.addr3.grid(row=row, column=1)

        row += 1

        #       City
        tk.Label(query_frame, text="City: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.addr_city = tk.Entry(query_frame, font=FONTS["m"])
        self.addr_city.grid(row=row, column=1)

        row += 1

        #       Post Code
        tk.Label(query_frame, text="Post Code: ", font=FONTS["m"]).grid(row=row, column=0, padx=10, sticky="e")
        self.addr_post = tk.Entry(query_frame, font=FONTS["m"])
        self.addr_post.grid(row=row, column=1)

        row += 1

        # Separate
        ttk.Separator(query_frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=5, padx=10)

        row += 1

        # Include all button
        tk.Label(query_frame, text="Results must include every field", wraplength=120, width=15,
                 font=FONTS["s"]).grid(row=row, column=0)

        self.include_all = tk.IntVar()
        tk.Checkbutton(query_frame, variable=self.include_all).grid(row=row, column=1, sticky="w", padx=10)

        row += 1

        # Separate
        ttk.Separator(query_frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=5, padx=10)

        row += 1

        # Exact
        tk.Label(query_frame, text="Fields must be exact", wraplength=120, width=15, font=FONTS["s"]).grid(
            row=row, column=0)

        self.exact_fields = tk.IntVar()
        tk.Checkbutton(query_frame, variable=self.exact_fields).grid(row=row, column=1, sticky="w", padx=10)

        row += 1

        # Search Button
        tk.Button(query_frame, text="Search", font=FONTS["m"], bg="#00dd00",
                  command=self.fetch_results).grid(row=row, column=0, columnspan=2, sticky="nsew", pady=20, padx=20)

    def fetch_results(self):
        """Fetch and show all the results"""
        cid = self.cust_id.get()
        fname = self.first_name.get()
        lname = self.last_name.get()

        addr = [self.addr1.get(),
                self.addr2.get(),
                self.addr3.get(),
                self.addr_city.get(),
                self.addr_post.get()]

        include_all = self.include_all.get()
        exact_field = self.exact_fields.get()

        if cid == "":
            cid = None
        else:
            try:
                cid = int(cid)
            except:
                self.cust_id.delete(0, tk.END)
                self.cust_id.insert(0, "Integers Only")
                cid = None

        if fname == "":
            fname = None

        if lname == "":
            lname = None

        if addr[0] == "":
            addr[0] = None

        if addr[1] == "":
            addr[1] = None

        if addr[2] == "":
            addr[2] = None

        if addr[3] == "":
            addr[3] = None

        if addr[4] == "":
            addr[4] = None

        if include_all == 1:
            include_all = True
        else:
            include_all = False

        if exact_field == 1:
            exact_field = True
        else:
            exact_field = False

        results, reply = SYSTEM.search_customers(cid=cid, fname=fname, lname=lname, addr=addr,
                                          must_include_all=include_all, exact=exact_field)

        # Wipe any previous results or data
        for child in self.results_frame.winfo_children():
            child.destroy()

        # Report any reason why there is no results
        if len(results) == 0:
            tk.Label(self.results_frame, text=reply, font=FONTS["m"], fg="#dd0000").pack(side="top", fill="x")
        else:
            row = 0
            for cust in results:
                tk.Label(self.results_frame, font=FONTS["m"],
                         text=f"{cust.customer_id}:").grid(row=row, column=0, sticky="w", padx=5)
                tk.Label(self.results_frame, font=FONTS["m"],
                         text=f"{cust.first_name} {cust.last_name}").grid(row=row, column=1, sticky="w", padx=5)
                tk.Label(self.results_frame, font=FONTS["m"],
                         text=f"{cust.address[0][0:10]}.. {cust.address[4]}").grid(row=row, column=2, sticky="w", padx=5)

                tk.Button(self.results_frame, text="View Customer", font=FONTS["m"],
                          command=lambda cid=cust.customer_id: self.view_customer(cid)).grid(row=row, column=4, padx=5,
                                                                                             sticky="nsew")

                row += 1

    def view_customer(self, customer_id: int):
        """Opens the customer page and sets it up to view the customer with given id"""
        self.controller.Pages[CustomerView.__name__].load_customer_info(customer_id)
        self.controller.show_page(CustomerView.__name__)


class CustomerCreate(PageBase):
    """Page for creating a new customer"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="New Customer", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Required fields notice
        tk.Label(self, text="All fields with * are required.",
                 font=FONTS["s"], fg="#dd0000").pack(side="top")

        # Required fields notice
        self.fail_text = tk.Label(self, text="",
                 font=FONTS["s"], fg="#dd0000")
        self.fail_text.pack(side="top")

        # Input parent frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y", pady=30)

        # Name
        tk.Label(input_frame, text="Name: ", font=FONTS["m"]).grid(row=1, column=0, sticky="e")
        tk.Label(input_frame, text="First *", font=FONTS["m"]).grid(row=0, column=1, sticky="w")
        tk.Label(input_frame, text="Last *", font=FONTS["m"]).grid(row=0, column=2, sticky="w")

        self.first_name = tk.Entry(input_frame, font=FONTS["m"])
        self.first_name.grid(row=1, column=1, sticky="nsew", padx=5)
        self.last_name = tk.Entry(input_frame, font=FONTS["m"])
        self.last_name.grid(row=1, column=2, sticky="nsew", padx=5)

        ttk.Separator(input_frame).grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        # Address
        tk.Label(input_frame, text="Address", font=FONTS["m"]).grid(row=3, column=0, columnspan=3, sticky="nsew", pady=5)

        # Line 1
        tk.Label(input_frame, text="Line 1 *", font=FONTS["m"]).grid(row=4, column=0, sticky="w")

        self.addr_l1 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l1.grid(row=4, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line 2
        tk.Label(input_frame, text="Line 2", font=FONTS["m"]).grid(row=5, column=0, sticky="w")

        self.addr_l2 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l2.grid(row=5, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line 3
        tk.Label(input_frame, text="Line 3", font=FONTS["m"]).grid(row=6, column=0, sticky="w")

        self.addr_l3 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l3.grid(row=6, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line city
        tk.Label(input_frame, text="City *", font=FONTS["m"]).grid(row=7, column=1, sticky="ew")

        self.addr_city = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_city.grid(row=8, column=1, sticky="nsew", padx=5)

        # Line Post code
        tk.Label(input_frame, text="Postcode *", font=FONTS["m"]).grid(row=7, column=2, sticky="ew")

        self.addr_post = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_post.grid(row=8, column=2, sticky="nsew", padx=5)

        # Submit button
        tk.Button(input_frame, text="Submit", font=FONTS["m"], bg="#00dd00",
                  command=self.submit).grid(row=9, column=1, columnspan=2, sticky="nsew", pady=30, padx=5)

    def submit(self):
        """Run when the form is submitted"""
        fname = self.first_name.get()
        lname = self.last_name.get()

        addr = [self.addr_l1.get(),
                self.addr_l2.get(),
                self.addr_l3.get(),
                self.addr_city.get(),
                self.addr_post.get()]

        run_query = True

        # Check the required fields
        if len(fname) == 0:
            self.first_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if len(lname) == 0:
            self.last_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if len(addr[0]) == 0:
            self.addr_l1.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if len(addr[3]) == 0:
            self.addr_city.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if len(addr[4]) == 0:
            self.addr_post.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        # Run the query if all required_data is set
        if run_query:
            status, reply, cid = SYSTEM.create_new_customer(fname, lname, addr)
            if status:
                self.controller.Pages[CustomerView.__name__].load_customer_info(cid)
                self.controller.show_page(CustomerView.__name__)
            else:
                self.fail_text.configure(text=reply)

    def page_update(self):
        """Runs when the page is displayed"""
        self.first_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.last_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_l1.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_city.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_post.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.fail_text.configure(text="")


class CustomerView(PageBase):
    """View a customer and all their data"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Customer Information", font=FONTS["l"]).pack(side="top", fill="x", pady=15)

        # Warning text
        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="y", pady=15)

        # TODO: Make a button to navigate to information update page

        data_frame = tk.Frame(self)
        data_frame.pack(side="top", fill="y")

        # Name
        tk.Label(data_frame, text="Name: ", font=FONTS["m"]).grid(row=0, column=0, sticky="nsw")

        self.first_name_lbl = tk.Label(data_frame, text="Cain", font=FONTS["m"])
        self.first_name_lbl.grid(row=0, column=1, sticky="nsw")

        self.last_name_lbl = tk.Label(data_frame, text="Ashmore", font=FONTS["m"])
        self.last_name_lbl.grid(row=0, column=2, sticky="nsw")

        # Address
        tk.Label(data_frame, text="Address: ", font=FONTS["m"]).grid(row=1, column=0, sticky="nsw")

        self.address_l1_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.address_l2_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.address_l3_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.address_city_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.address_post_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.address_l1_lbl.grid(row=1, column=1, columnspan=2, sticky="nsw")
        self.address_l2_lbl.grid(row=2, column=1, columnspan=2, sticky="nsw")
        self.address_l3_lbl.grid(row=3, column=1, columnspan=2, sticky="nsw")
        self.address_city_lbl.grid(row=4, column=1, columnspan=2, sticky="nsw")
        self.address_post_lbl.grid(row=5, column=1, columnspan=2, sticky="nsw")


        # Accounts
        accounts_frame = tk.LabelFrame(data_frame, text="Accounts", font=FONTS["s"])
        accounts_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")

        scrollFrame = ScrollableFrame(accounts_frame)
        scrollFrame.grid(row=7, column=0, columnspan=4, sticky="nsew")

        self.accounts_parent = scrollFrame.widget_frame

    def load_customer_info(self, customer_id: int):
        """Load the customer information onto the page"""
        cust_data = SYSTEM.get_customer_data(customer_id)
        customer = cust_data['customer']
        accounts = cust_data['accounts']

        if customer is None:
            self.fail_text.configure(text=f"Customer with id {str(customer_id)} could not be found")

            self.first_name_lbl.configure(text="")
            self.last_name_lbl.configure(text="")

            self.address_l1_lbl.configure(text="")
            self.address_l2_lbl.configure(text="")
            self.address_l3_lbl.configure(text="")
            self.address_city_lbl.configure(text="")
            self.address_post_lbl.configure(text="")
        else:
            self.fail_text.configure(text="")

            self.first_name_lbl.configure(text=customer.get_first_name())
            self.last_name_lbl.configure(text=customer.get_last_name())

            addr = customer.get_address()

            self.address_l1_lbl.configure(text=addr[0])
            self.address_l2_lbl.configure(text=addr[1])
            self.address_l3_lbl.configure(text=addr[2])
            self.address_city_lbl.configure(text=addr[3])
            self.address_post_lbl.configure(text=addr[4])

        # Clear all the currently held accounts from the accounts parent
        for child in self.accounts_parent.winfo_children():
            child.destroy()

        # populate the accounts_parent
        row = 0
        for account in accounts:
            # name
            tk.Label(self.accounts_parent, text=account.account_name + ": ", font=FONTS["s"]).grid(row=row, column=0, sticky="w", padx=5)

            # Balance
            tk.Label(self.accounts_parent, text="£" + str((account.balance/100)), font=FONTS["s"]).grid(row=row, column=1, sticky="w", padx=5)

            # Interest Rate
            tk.Label(self.accounts_parent, text=str(account.interest_rate) + "%", font=FONTS["s"]).grid(row=row, column=2, sticky="w", padx=5)

            # View button
            tk.Button(self.accounts_parent, text="View account", font=FONTS["s"],
                      command=lambda accid=account.account_id: self.view_account(accid)).grid(row=row, column=3, padx=5)

            row += 1

    def view_account(self, account_id: int):
        """Set the account view up for the account with the given id and then show the account"""
        page = self.controller.Pages[AccountView.__name__]
        page.load_account_info(account_id)
        self.controller.show_page(AccountView.__name__)


class AccountView(PageBase):
    """View page for details about an account"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Account Information", font=FONTS["l"]).pack(side="top", fill="x", pady=15)

        # TODO: Add buttons to take us too update, transfer, withdraw etc
        # Warning text
        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="y", pady=15)

        # Data section
        data_frame = tk.Frame(self)
        data_frame.pack(side="top", fill="y")

        # Account Name
        tk.Label(data_frame, text="Account Name: ", font=FONTS["m"]).grid(row=0, column=0, sticky="w")
        self.account_name_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.account_name_lbl.grid(row=0, column=1, sticky="w")

        # Account Balance
        tk.Label(data_frame, text="Balance: ", font=FONTS["m"]).grid(row=1, column=0, sticky="w")
        self.balance_lbl = tk.Label(data_frame, text="£-.--", font=FONTS["m"])
        self.balance_lbl.grid(row=1, column=1, sticky="w")

        # Account overdraft
        tk.Label(data_frame, text="Overdraft limit: ", font=FONTS["m"]).grid(row=2, column=0, sticky="w")
        self.overdraft_lbl = tk.Label(data_frame, text="£-.--", font=FONTS["m"])
        self.overdraft_lbl.grid(row=2, column=1, sticky="w")

        # Account interest rate
        tk.Label(data_frame, text="Interest rate: ", font=FONTS["m"]).grid(row=3, column=0, sticky="w")
        self.interest_lbl = tk.Label(data_frame, text="-.-%", font=FONTS["m"])
        self.interest_lbl.grid(row=3, column=1, sticky="w")

        # Account Holder
        tk.Label(data_frame, text="Account Holder: ", font=FONTS["m"]).grid(row=4, column=0, sticky="w")
        self.account_holder_lbl = tk.Label(data_frame, text="-.-%", font=FONTS["m"])
        self.account_holder_lbl.grid(row=4, column=1, sticky="w")

        self.customer_view_btn = tk.Button(data_frame, text="View Account", font=FONTS["m"])
        self.customer_view_btn.grid(row=4, column=2, sticky="nsew")

    def load_account_info(self, account_id: int):
        """Load account information into the page from the account connected to the given id"""
        account = SYSTEM.get_account_data(account_id)

        if account is None:
            self.fail_text.configure(text=f"Account with id {account_id} could not be found.")

            self.account_name_lbl.configure(text="")
            self.balance_lbl.configure(text="£-.--")
            self.overdraft_lbl.configure(text="£-.--")
            self.interest_lbl.configure(text="-.--%")
            self.account_holder_lbl.configure(text="")
            self.customer_view_btn.configure(command=lambda: print(end=""))
        else:
            self.fail_text.configure(text="")

            self.account_name_lbl.configure(text=f"{account.account_name}")
            self.balance_lbl.configure(text=f"£{account.balance/100}")
            self.overdraft_lbl.configure(text=f"£{account.overdraft_limit/100}")
            self.interest_lbl.configure(text=f"{account.interest_rate}%")
            self.account_holder_lbl.configure(text=f"{account.customer.first_name} {account.customer.last_name}")
            self.customer_view_btn.configure(command=lambda: self.view_customer(account.customer.customer_id))

    def view_customer(self, customer_id: int):
        """Opens the customer page and sets it up to view the customer with given id"""
        self.controller.Pages[CustomerView.__name__].load_customer_info(customer_id)
        self.controller.show_page(CustomerView.__name__)


if __name__ == "__main__":
    win = Window()
    win.mainloop()

