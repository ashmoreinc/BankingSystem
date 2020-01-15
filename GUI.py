import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmb

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
        for page in PageBase.__subclasses__():  # Populate with pages
            # Fetch all the subclasses of PageBase as all pages will inherit from this
            p = page(container, self)

            self.Pages[page.__name__] = p
            p.grid(row=0, column=0, sticky="nsew")

            p.initialise()
        self.show_page(LoginPage.__name__)

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
    tk.Button(header_frame, text="Your Account", font=FONTS["m"],
              command=lambda: window_controller.show_page(AdminView.__name__)).pack(side="right", fill="y")

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
        """To be overridden with tasks that must be completed on class initialisation by the controller class Window"""
        pass

    def page_update(self):
        """To be overridden with tasks that must be completed when this page is switched too"""

    pass


class LoginPage(PageBase):
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

        # Bind the enter/return key to the login function. UX so that the user can press enter instead of button press.
        self.password_entry.bind("<Return>", lambda event: self.login())

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

    def page_update(self):
        """Runs when the page is shown"""
        # Clear all input fields so they aren't stored for when the system has been logged out of
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        # Put the focus on the username field
        self.username_entry.focus()


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

        # Customer Control
        cust_manage = tk.Frame(customer_frame)
        cust_manage.pack(side="top", fill="both", expand=True)

        tk.Label(cust_manage, text="Customer Management", font=FONTS["l"]).grid(row=0, column=0, columnspan=2)

        # Customer Buttons
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

        # Account Buttons
        tk.Button(account_manage, text="Search", font=FONTS["m"],
                  command=lambda: controller.show_page(AccountSearch.__name__)).grid(row=1, column=0, sticky="w")

        tk.Button(account_manage, text="Create", font=FONTS["m"],
                  command=lambda: controller.show_page(AccountCreate.__name__)).grid(row=1, column=1, sticky="w")

        tk.Button(account_manage, text="Money Transfer", font=FONTS["m"],
                  command=lambda: controller.show_page(AccountTransfer.__name__)).grid(row=1, column=2, sticky="w")

        tk.Button(account_manage, text="Deposit/Withdraw", font=FONTS["m"],
                  command=lambda: controller.show_page(AccountDepositWithdraw.__name__)).grid(row=1, column=3,
                                                                                              sticky="w")
        # Reports section
        tk.Button(reports_frame, text="Full report", font=FONTS["m"],
                  command=lambda: controller.show_page(ReportAll.__name__)).pack(side="top", fill="x")

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
        row = 0  # Use a row variable so we can quickly add widgets in and swap them easily without hardcoded rows

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

        row += 1
        # Get all customers
        tk.Button(query_frame, text="View All", font=FONTS["m"], bg="#00aa00",
                  command=lambda: self.fetch_results(get_all=True)).grid(row=row, column=0, columnspan=2, sticky="nsew", pady=20, padx=20)

    def fetch_results(self, get_all=False):
        """Fetch and show all the results"""
        if not get_all:
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
        else:
            results, reply = SYSTEM.search_customers(get_all=get_all)

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
                         text=f"{cust.address[0][0:10]}.. {cust.address[4]}").grid(row=row, column=2, sticky="w",
                                                                                   padx=5)

                tk.Button(self.results_frame, text="View Customer", font=FONTS["m"],
                          command=lambda cid=cust.customer_id: self.view_customer(cid)).grid(row=row, column=4, padx=5,
                                                                                             sticky="nsew")

                row += 1

    def view_customer(self, customer_id: int):
        """Opens the customer page and sets it up to view the customer with given id"""
        self.controller.Pages[CustomerView.__name__].load_customer_info(customer_id)
        self.controller.show_page(CustomerView.__name__)

    def page_update(self):
        """Runs when this page is displayed"""
        # Wipe any previous searches
        for child in self.results_frame.winfo_children():
            child.destroy()

        # Empty all the input fields
        self.cust_id.delete(0, tk.END)
        self.first_name.delete(0, tk.END)
        self.last_name.delete(0, tk.END)
        self.addr1.delete(0, tk.END)
        self.addr2.delete(0, tk.END)
        self.addr3.delete(0, tk.END)
        self.addr_city.delete(0, tk.END)
        self.addr_post.delete(0, tk.END)


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

        # Text shown on failure
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
        tk.Label(input_frame, text="Address", font=FONTS["m"]).grid(row=3, column=0, columnspan=3, sticky="nsew",
                                                                    pady=5)

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


class CustomerUpdate(PageBase):
    """Update form for customer information"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # This will be used to hold data about the customer being edited
        self.current_customer = None

        # Page widgets
        create_navigation_bar(self, controller)

        # title
        tk.Label(self, text="Customer edit", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Required fields notice
        tk.Label(self, text="All fields with * are to be filled.",
                 font=FONTS["s"], fg="#dd0000").pack(side="top")

        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="x")

        # Input parent frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y", pady=30)

        # Id (not editable)
        tk.Label(input_frame, text="Customer ID: ", font=FONTS["m"]).grid(row=0, column=0, sticky="e")

        self.customer_id = tk.Label(input_frame, text="", font=FONTS["m"])
        self.customer_id.grid(row=0, column=1, sticky="w")

        # Name
        tk.Label(input_frame, text="Name: ", font=FONTS["m"]).grid(row=2, column=0, sticky="e")
        tk.Label(input_frame, text="First *", font=FONTS["m"]).grid(row=1, column=1, sticky="w")
        tk.Label(input_frame, text="Last *", font=FONTS["m"]).grid(row=1, column=2, sticky="w")

        self.first_name = tk.Entry(input_frame, font=FONTS["m"])
        self.first_name.grid(row=2, column=1, sticky="nsew", padx=5)
        self.last_name = tk.Entry(input_frame, font=FONTS["m"])
        self.last_name.grid(row=2, column=2, sticky="nsew", padx=5)

        ttk.Separator(input_frame).grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        # Address
        tk.Label(input_frame, text="Address", font=FONTS["m"]).grid(row=4, column=0, columnspan=3, sticky="nsew",
                                                                    pady=5)

        # Line 1
        tk.Label(input_frame, text="Line 1 *", font=FONTS["m"]).grid(row=5, column=0, sticky="w")

        self.addr_l1 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l1.grid(row=5, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line 2
        tk.Label(input_frame, text="Line 2", font=FONTS["m"]).grid(row=6, column=0, sticky="w")

        self.addr_l2 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l2.grid(row=6, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line 3
        tk.Label(input_frame, text="Line 3", font=FONTS["m"]).grid(row=7, column=0, sticky="w")

        self.addr_l3 = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l3.grid(row=7, column=1, columnspan=2, sticky="nsew", pady=2, padx=10)

        # Line city
        tk.Label(input_frame, text="City *", font=FONTS["m"]).grid(row=8, column=1, sticky="ew")

        self.addr_city = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_city.grid(row=9, column=1, sticky="nsew", padx=5)

        # Line Post code
        tk.Label(input_frame, text="Postcode *", font=FONTS["m"]).grid(row=8, column=2, sticky="ew")

        self.addr_post = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_post.grid(row=9, column=2, sticky="nsew", padx=5)

        # Submit button
        tk.Button(input_frame, text="Update", font=FONTS["m"], bg="#00dd00",
                  command=self.update_info).grid(row=10, column=1, columnspan=2, sticky="nsew", pady=30, padx=5)

        # Delete button
        tk.Button(self, text="Delete Customer", font=FONTS["m"], bg="#dd0000",
                  command=self.delete_customer).pack(side="bottom", pady=10)

    def delete_customer(self):
        """Delete the customer from the system"""
        if self.current_customer is not None:
            # Check if the admin is sure of their choice
            answer = tkmb.askyesno("Deleting customer.",
                                   "Are you sure you would like to delete this customer "
                                   "and all accounts associated with it?")
            if answer:
                cust_data = SYSTEM.get_customer_data(customer_id=self.current_customer.customer_id)
                accounts = cust_data["accounts"]

                total_refunded = 0

                for account in accounts:
                    total_refunded += account.balance

                if total_refunded < 0:
                    tkmb.showinfo("Money owed", f"This customer owes £{(total_refunded * -1) / 100}.")
                else:
                    tkmb.showinfo("Refund", f"This customer needs £{(total_refunded) / 100} refunded.")

                # Delete the customer entry via the BankSystem handler

                status, reply = SYSTEM.delete_customer(self.current_customer.customer_id)

                if status:
                    self.controller.show_page(LandingPage.__name__)
                else:
                    tkmb.showerror("Could not delete accounts", f"Reason: {reply}")
            else:
                tkmb.showinfo("Deletion cancelled", "The account has not been deleted.")

        else:
            tkmb.showerror("Customer selection error", "No customer has been selected.")

    def update_info(self):
        """Gets the inputs, verifies the data, then sends the update to the system"""
        fname = self.first_name.get()
        lname = self.last_name.get()

        addr = [self.addr_l1.get(),
                self.addr_l2.get(),
                self.addr_l3.get(),
                self.addr_city.get(),
                self.addr_post.get()]

        run_query = True
        kwargs = {}

        if len(fname) == 0:
            run_query = False
            self.first_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.first_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
            kwargs['fname'] = fname

        if len(lname) == 0:
            run_query = False
            self.last_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.last_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
            kwargs['lname'] = lname

        if len(addr[0]) == 0:
            run_query = False
            self.addr_l1.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_l1.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)

        if len(addr[3]) == 0:
            run_query = False
            self.addr_city.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_city.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)

        if len(addr[4]) == 0:
            run_query = False
            self.addr_post.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_post.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)

        kwargs['addr'] = addr

        if run_query:
            status, reply, customers = SYSTEM.update_customer(self.current_customer.customer_id, **kwargs)
            customer = customers[0]

            if status:
                # Set the current customer
                self.current_customer = customer

                # Take the customer back to the customer view page with the updated customer details
                self.controller.Pages[CustomerView.__name__].load_customer_info(self.current_customer.customer_id)
                self.controller.show_page(CustomerView.__name__)
            else:
                self.fail_text.configure(text=reply)
        else:
            self.fail_text.configure(text="All fields marked * must be set.")

    def load_data_into_entry(self):
        """Loads all the data from the customer into the entry boxes"""
        # Clear the data
        self.first_name.delete(0, tk.END)
        self.last_name.delete(0, tk.END)

        self.addr_l1.delete(0, tk.END)
        self.addr_l2.delete(0, tk.END)
        self.addr_l3.delete(0, tk.END)
        self.addr_city.delete(0, tk.END)
        self.addr_post.delete(0, tk.END)

        if self.current_customer is not None:
            self.customer_id.configure(text=str(self.current_customer.customer_id), fg="#000000")

            self.first_name.insert(0, self.current_customer.first_name)
            self.last_name.insert(0, self.current_customer.last_name)

            self.addr_l1.insert(0, self.current_customer.address[0])
            if self.current_customer.address[1] is None:
                self.current_customer.address[1] = ""
            self.addr_l2.insert(0, self.current_customer.address[1])
            if self.current_customer.address[2] is None:
                self.current_customer.address[2] = ""
            self.addr_l3.insert(0, self.current_customer.address[2])
            self.addr_city.insert(0, self.current_customer.address[3])
            self.addr_post.insert(0, self.current_customer.address[4])
        else:
            self.customer_id.configure(text="Customer is not set", fg="#dd0000")

    def set_customer(self, customer):
        """Sets the customer to work with"""
        self.current_customer = customer

    def page_update(self):
        """Runs when the page is shown"""
        self.load_data_into_entry()

        self.first_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.last_name.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_post.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_city.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)
        self.addr_l1.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=0)


class CustomerView(PageBase):
    """View a customer and all their data"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.current_customer = None

        create_navigation_bar(self, controller)

        # Title
        header = tk.Frame(self)
        header.pack(side="top", pady=15)

        tk.Label(header, text="Customer Information", font=FONTS["l"]).grid(row=0, column=0, sticky="nsew")

        # Update button
        tk.Button(header, text="Update Customer", font=FONTS["m"],
                  command=self.update_customer).grid(row=1, column=0, sticky="nsew")

        # Warning text
        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="y", pady=15)

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

        scrollframe = ScrollableFrame(accounts_frame)
        scrollframe.grid(row=7, column=0, columnspan=4, sticky="nsew")

        self.accounts_parent = scrollframe.widget_frame

    def load_customer_info(self, customer_id: int):
        """Load the customer information onto the page"""
        cust_data = SYSTEM.get_customer_data(customer_id)
        customer = cust_data['customer']
        accounts = cust_data['accounts']

        self.current_customer = customer

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
            tk.Label(self.accounts_parent, text=account.account_name + ": ", font=FONTS["s"]).grid(row=row, column=0,
                                                                                                   sticky="w", padx=5)

            # Balance
            tk.Label(self.accounts_parent, text="£" + str((account.balance / 100)), font=FONTS["s"]).grid(row=row,
                                                                                                          column=1,
                                                                                                          sticky="w",
                                                                                                          padx=5)

            # Interest Rate
            tk.Label(self.accounts_parent, text=str(account.interest_rate) + "%", font=FONTS["s"]).grid(row=row,
                                                                                                        column=2,
                                                                                                        sticky="w",
                                                                                                        padx=5)

            # View button
            tk.Button(self.accounts_parent, text="View account", font=FONTS["s"],
                      command=lambda accid=account.account_id: self.view_account(accid)).grid(row=row, column=3, padx=5)

            row += 1

    def update_customer(self):
        """Go to the customer update page for this customer"""
        if self.current_customer is None:
            tkmb.showerror("Customer Error.", "No customer is currently selected. Please go to Home and try again.")
        else:
            self.controller.Pages[CustomerUpdate.__name__].set_customer(self.current_customer)
            self.controller.show_page(CustomerUpdate.__name__)

    def view_account(self, account_id: int):
        """Set the account view up for the account with the given id and then show the account"""
        page = self.controller.Pages[AccountView.__name__]
        page.load_account_info(account_id)
        self.controller.show_page(AccountView.__name__)


class AccountSearch(PageBase):
    """Search page for navigating accounts"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Search Accounts", font=FONTS["l"]).pack(side="top", fill="x", pady=10)

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

        # Inputs
        row = 0

        # Customer Name
        tk.Label(query_frame, text="First Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.first_name = tk.Entry(query_frame, font=FONTS["m"])
        self.first_name.grid(row=row, column=1)

        row += 1

        tk.Label(query_frame, text="Last Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.last_name = tk.Entry(query_frame, font=FONTS["m"])
        self.last_name.grid(row=row, column=1)

        row += 1

        # Separator
        ttk.Separator(query_frame).grid(row=row, column=0, columnspan=3, sticky="ew", pady=5, padx=10)

        row += 1

        # Account Details
        # ID
        tk.Label(query_frame, text="Account ID: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.account_id = tk.Entry(query_frame, font=FONTS["m"])
        self.account_id.grid(row=row, column=1)

        row += 1

        # name
        tk.Label(query_frame, text="Account Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.account_name = tk.Entry(query_frame, font=FONTS["m"])
        self.account_name.grid(row=row, column=1)

        row += 1

        # account number
        tk.Label(query_frame, text="Account Number: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.account_number = tk.Entry(query_frame, font=FONTS["m"])
        self.account_number.grid(row=row, column=1)

        row += 1

        # Separator
        ttk.Separator(query_frame).grid(row=row, column=0, columnspan=3, sticky="ew", pady=5, padx=10)

        row += 1

        # Balance Details
        # balance
        tk.Label(query_frame, text="Balance: £", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.balance = tk.Entry(query_frame, font=FONTS["m"])
        self.balance.grid(row=row, column=1)

        #   balance options, >, =, <
        row += 1
        opts_frame = tk.Frame(query_frame)
        opts_frame.grid(row=row, column=1, sticky="nsew")

        self.balance_opts = tk.StringVar()
        self.balance_opts.set("=")

        tk.Radiobutton(opts_frame, text=">", variable=self.balance_opts,
                       value=">", font=FONTS["m"]).grid(row=0, column=0, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="=", variable=self.balance_opts,
                       value="=", font=FONTS["m"]).grid(row=0, column=2, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=3, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="<", variable=self.balance_opts,
                       value="<", font=FONTS["m"]).grid(row=0, column=4, sticky="ew")

        row += 1

        # overdraft
        tk.Label(query_frame, text="Overdraft: £", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.overdraft = tk.Entry(query_frame, font=FONTS["m"])
        self.overdraft.grid(row=row, column=1)

        #   overdraft options, >, =, <
        row += 1
        opts_frame = tk.Frame(query_frame)
        opts_frame.grid(row=row, column=1, sticky="nsew")

        self.overdraft_opts = tk.StringVar()
        self.overdraft_opts.set("=")

        tk.Radiobutton(opts_frame, text=">", variable=self.overdraft_opts,
                       value=">", font=FONTS["m"]).grid(row=0, column=0, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="=", variable=self.overdraft_opts,
                       value="=", font=FONTS["m"]).grid(row=0, column=2, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=3, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="<", variable=self.overdraft_opts,
                       value="<", font=FONTS["m"]).grid(row=0, column=4, sticky="ew")

        row += 1

        # Interest Rate
        tk.Label(query_frame, text="Interest Rate: %", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.interest = tk.Entry(query_frame, font=FONTS["m"])
        self.interest.grid(row=row, column=1)

        #   overdraft options, >, =, <
        row += 1
        opts_frame = tk.Frame(query_frame)
        opts_frame.grid(row=row, column=1, sticky="nsew")

        self.interest_opts = tk.StringVar()
        self.interest_opts.set("=")

        tk.Radiobutton(opts_frame, text=">", variable=self.interest_opts,
                       value=">", font=FONTS["m"]).grid(row=0, column=0, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="=", variable=self.interest_opts,
                       value="=", font=FONTS["m"]).grid(row=0, column=2, sticky="ew")

        ttk.Separator(opts_frame, orient="vertical").grid(row=0, column=3, sticky="ns", padx=5, pady=5)

        tk.Radiobutton(opts_frame, text="<", variable=self.interest_opts,
                       value="<", font=FONTS["m"]).grid(row=0, column=4, sticky="ew")

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
        # search button
        tk.Button(query_frame, text="Search", font=FONTS["m"], bg="#00dd00",
                  command=self.fetch_results).grid(row=row, column=0, columnspan=2, sticky="nsew", pady=2)

        row += 1

        # View all
        tk.Button(query_frame, text="View All", font=FONTS["m"], bg="#00dd00",
                  command=lambda: self.fetch_results(get_all=True)).grid(row=row, column=0, columnspan=2,
                                                                         sticky="nsew", pady=2)

    def fetch_results(self, get_all=False):
        """Fetch's and displays all results"""
        kwargs = {}

        def check_fill(param_name, inp, type=str):
            """Checks if a input is valid and adds it to the kwargs dict if it is"""
            if len(inp) > 0:
                try:
                    inp = type(inp)
                    kwargs[param_name] = inp
                except:
                    print(f"Could not convert '{inp}' to '{str(type)}'")
        if get_all:
            accounts, reply = SYSTEM.search_accounts(get_all=True)
        else:
            kwargs = {}
            fname = self.first_name.get()
            check_fill('cust_first', fname)

            lname = self.last_name.get()
            check_fill('cust_last', lname)

            acc_id = self.account_id.get()
            check_fill('accid', acc_id, type=int)

            acc_name = self.account_name.get()
            check_fill('account_name', acc_name)

            acc_num = self.account_number.get()
            check_fill('account_number', acc_num, type=int)

            balance = self.balance.get()
            check_fill('balance', balance, type=int)
            # Convert the input into pence, as that is how the data is stored
            if 'balance' in kwargs:
                kwargs['balance'] = kwargs['balance'] * 100
            balance_opt = self.balance_opts.get()
            check_fill('balance_opts', balance_opt)

            overdraft = self.overdraft.get()
            check_fill('overdraft_limit', overdraft, type=int)
            # Convert the input into pence, as that is how the data is stored
            if 'overdraft_limit' in kwargs:
                kwargs['overdraft_limit'] = kwargs['overdraft_limit'] * 100
            overdraft_opt = self.overdraft_opts.get()
            check_fill('overdraft_opts', overdraft_opt)

            interest = self.interest.get()
            check_fill('interest_rate', interest, type=float)
            interest_opt = self.interest_opts.get()
            check_fill('interest_opts', interest_opt)

            # We can use bool() on these as they are intvars with values of 1 or 0
            include_all = bool(self.include_all.get())
            exact_field = bool(self.exact_fields.get())

            kwargs["exact_fields"] = exact_field
            kwargs["must_include_all"] = include_all

            accounts, reply = SYSTEM.search_accounts(**kwargs)

        # Clear the results frame
        for child in self.results_frame.winfo_children():
            child.destroy()

        # Display the result
        if len(accounts) < 1:
            tk.Label(self.results_frame, text=reply, font=FONTS["m"], fg="#dd0000").pack(side="top", fill="x")
        else:
            row = 0
            for account in accounts:
                # ID
                tk.Label(self.results_frame, text=f"{account.account_id}: ",
                         font=FONTS["m"]).grid(row=row, column=0, sticky="w", padx=5)

                # Account Name
                tk.Label(self.results_frame, text=f"{account.account_name}",
                         font=FONTS["m"]).grid(row=row, column=1, sticky="w", padx=5)

                # Account Customer Name
                tk.Label(self.results_frame, text=f"{account.customer.first_name}  {account.customer.last_name}",
                         font=FONTS["m"]).grid(row=row, column=2, sticky="w", padx=5)

                # Account Balance
                tk.Label(self.results_frame, text=f"£{account.balance/100}",
                         font=FONTS["m"]).grid(row=row, column=3, sticky="w", padx=5)

                # Show account button
                tk.Button(self.results_frame, text="View Account", font=FONTS["m"],
                          command=lambda aid=account.account_id: self.show_account(aid)).grid(row=row, column=4,
                                                                                              sticky="nsew")

                row += 1

    def show_account(self, account_id):
        """Load the account view page with the customer given and then show that page"""
        self.controller.Pages[AccountView.__name__].load_account_info(account_id)
        self.controller.show_page(AccountView.__name__)

    def page_update(self):
        """Runs when the page is shown"""
        # Clear the results frame
        for child in self.results_frame.winfo_children():
            child.destroy()


class AccountCreate(PageBase):
    """Create an account page"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="New Account", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Text shown on failure
        self.fail_text = tk.Label(self, text="",
                                  font=FONTS["s"], fg="#dd0000")
        self.fail_text.pack(side="top")

        # Input parent frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y", pady=30)

        row = 0

        # Customer ID
        tk.Label(input_frame, text="Customer ID: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.cust_id_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.cust_id_ent.grid(row=row, column=1, sticky="nsew", pady=5)

        row += 1

        # Account name
        tk.Label(input_frame, text="Account Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.acc_name_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.acc_name_ent.grid(row=row, column=1, sticky="nsew", pady=5)

        row += 1

        # Account Number Generator
        tk.Label(input_frame, text="Account Number: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.account_num = None

        self.acc_num_lbl = tk.Label(input_frame, text="", font=FONTS["m"])
        self.acc_num_lbl.grid(row=row, column=1, sticky="w", pady=5)

        tk.Button(input_frame, text="Generate New", font=FONTS["m"],
                  command=self.generate_new_acc_num).grid(row=row, column=2, sticky="nsew", pady=5)

        row += 1

        # Interest Rate
        tk.Label(input_frame, text="Interest Rate: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        f = tk.Frame(input_frame)
        f.grid(row=row, column=1, sticky="nsew", pady=5)

        self.interest_ent = tk.Entry(f, font=FONTS["m"])
        self.interest_ent.grid(row=0, column=0, sticky="nsew", pady=5)

        tk.Label(f, text="%", font=FONTS["m"]).grid(row=0, column=1, sticky="w", pady=5)

        row += 1

        # Overdraft
        tk.Label(input_frame, text="Overdraft Limit: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        f = tk.Frame(input_frame)
        f.grid(row=row, column=1, sticky="nsew", pady=5)

        tk.Label(f, text="£", font=FONTS["m"]).grid(row=0, column=0, sticky="e", pady=5)

        self.overdraft_ent = tk.Entry(f, font=FONTS["m"])
        self.overdraft_ent.grid(row=0, column=1, sticky="nsew", pady=5)

        row += 1

        # Submit
        tk.Button(input_frame, text="Submit", font=FONTS["m"], bg="#00dd00",
                  command=self.submit).grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    def generate_new_acc_num(self):
        """Gets a new account number and shows that instead"""
        num = SYSTEM.generate_new_account_number()

        self.account_num = num

        num = str(num)
        account_string = num[0:4] + " " + num[4:8] + " " + num[8:12] + " " + num[12:]

        self.acc_num_lbl.configure(text=account_string)

    def submit(self):
        """Runs when the submit button is pressed."""
        cust_id = self.cust_id_ent.get()

        acc_name = self.acc_name_ent.get()
        acc_num = self.account_num

        interest = self.interest_ent.get()
        overdraft = self.overdraft_ent.get()

        run = True

        # Validity check
        if len(cust_id) == 0:
            self.fail_text.configure(text="All fields must be filled and properly formatted.")
            self.cust_id_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                       highlightthickness=2)

            run = False
        else:
            try:
                cust_id = int(cust_id)
            except:
                self.fail_text.configure(text="All fields must be filled and properly formatted.")
                self.cust_id_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                           highlightthickness=2)

                run = False

            data = SYSTEM.get_customer_data(customer_id=cust_id)

            if data["customer"] is None:
                self.fail_text.configure(text="Customer ID not connected to any accounts.")
                self.cust_id_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                           highlightthickness=2)
                # Break for this one so the user definitely sees this message.
                return
                run = False

        if len(acc_name) == 0:
            self.fail_text.configure(text="All fields must be filled and properly formatted.")
            self.acc_name_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                        highlightthickness=2)
            run = False
        else:
            self.acc_num_lbl.configure(highlightthickness=0)

        if acc_num is None:
            self.fail_text.configure(text="All fields must be filled.")
            self.generate_new_acc_num()
            run = False

        if len(interest) == 0:
            self.fail_text.configure(text="All fields must be filled and properly formatted.")
            self.interest_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                        highlightthickness=2)
            run = False
        else:
            try:
                interest = float(interest)
            except:
                self.fail_text.configure(text="All fields must be filled and properly formatted.")
                self.interest_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                            highlightthickness=2)
                run = False

        if len(overdraft) == 0:
            self.fail_text.configure(text="All fields must be filled and properly formatted.")
            self.overdraft_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                         highlightthickness=2)
            run = False
        else:
            try:
                overdraft = int(float(overdraft) * 100)
            except:
                self.fail_text.configure(text="All fields must be filled and properly formatted.")
                self.overdraft_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                             highlightthickness=2)
                run = False

        if run:
            self.fail_text.configure(text="")

            status, reply, accid = SYSTEM.create_new_account(acc_name, interest, overdraft,
                                                             cust_id, account_num=acc_num)

            if status:
                # Get the account
                account = SYSTEM.get_account_data(accid)

                # Go to account view page
                self.controller.Pages[AccountView.__name__].load_account_info(accid)
                self.controller.show_page(AccountView.__name__)

            else:
                self.fail_text.configure(text=reply)

    def page_update(self):
        """Runs on page show"""
        # Generate a new account number so that we aren't accidentally stuck on an old one
        self.generate_new_acc_num()


class AccountUpdate(PageBase):
    """Update and delete account information"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        self.current_account = None

        # Title
        tk.Label(self, text="Account Update", font=FONTS["l"]).pack(side="top", fill="x", pady=5)
        # Required fields notice
        tk.Label(self, text="All fields with * are to be filled.",
                 font=FONTS["s"], fg="#dd0000").pack(side="top")

        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="x")

        # Input frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y")

        row = 0

        # Account ID
        # Label
        tk.Label(input_frame, text="Account ID: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.account_id_lbl = tk.Label(input_frame, text="1", font=FONTS["m"])
        self.account_id_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        # Account Number
        tk.Label(input_frame, text="Account Number: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.account_num_lbl = tk.Label(input_frame, text="1111222233334444", font=FONTS["m"])
        self.account_num_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        # Balance:
        tk.Label(input_frame, text="Balance: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.balance_lbl = tk.Label(input_frame, text="£1000.00", font=FONTS["m"])
        self.balance_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        # Separator
        ttk.Separator(input_frame).grid(row=row, column=0, columnspan=3, sticky="nsew", padx=10)

        row += 1

        # Account name
        tk.Label(input_frame, text="Account Name *: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.account_name_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.account_name_ent.grid(row=row, column=1, sticky="nsew", pady=5)

        row += 1

        # Interest Rate
        tk.Label(input_frame, text="Interest Rate *: ", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.interest_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.interest_ent.grid(row=row, column=1, sticky="nsew", pady=5)

        tk.Label(input_frame, text="%", font=FONTS["m"]).grid(row=row, column=2, sticky="w", pady=5)

        row += 1

        # Overdraft Limit
        tk.Label(input_frame, text="Overdraft Limit *: £", font=FONTS["m"]).grid(row=row, column=0, sticky="e", pady=5)

        self.overdraft_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.overdraft_ent.grid(row=row, column=1, sticky="nsew", pady=5)

        # Submit button
        tk.Button(input_frame, text="Update", font=FONTS["m"], bg="#00dd00",
                  command=self.update_info).grid(row=10, column=0, columnspan=3, sticky="nsew", pady=30, padx=5)

        # Delete button
        tk.Button(self, text="Delete Customer", font=FONTS["m"], bg="#dd0000",
                  command=self.delete_account).pack(side="bottom", pady=10)

    def update_info(self):
        """Validates the data input and then updates the entry."""
        acc_name = self.account_name_ent.get()
        overdraft_limit = self.overdraft_ent.get()
        interest_rate = self.interest_ent.get()

        run_query = True
        kwargs = {}

        if len(acc_name) > 0:
            kwargs["account_name"] = acc_name
            self.account_name_ent.configure(highlightthickness=0)
        else:
            self.account_name_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                            highlightthickness=2)
            run_query = False

        if len(overdraft_limit) > 0:
            # Turn overdraft into a float, then an integer to represent the overdraft in pence,
            #   as that's how it is stored
            try:
                overdraft_limit = float(overdraft_limit)
                overdraft_limit = int(overdraft_limit * 100)
                kwargs["overdraft_limit"] = overdraft_limit
                self.overdraft_ent.configure(highlightthickness=0)
            except:
                tkmb.showerror("Input error.", "Overdraft entry must be a number only.")
                self.overdraft_ent.configure(highlightbackground="#dd0000",
                                             highlightcolor="#dd0000", highlightthickness=2)
                run_query = False
        else:
            self.overdraft_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if len(interest_rate) > 0:
            # Turn interest into a float.
            try:
                interest_rate = float(interest_rate)
                kwargs["interest_rate"] = interest_rate
                self.interest_ent.configure(highlightthickness=0)
            except:
                tkmb.showerror("Input error.", "Interest rate entry must be a number only.")
                self.interest_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000",
                                            highlightthickness=2)
                return
        else:
            self.interest_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
            run_query = False

        if run_query:
            status, reply, account = SYSTEM.update_account(self.current_account.account_id, **kwargs)

            if status:
                self.current_account = account

                self.controller.Pages[AccountView.__name__].load_account_info(self.current_account.account_id)
                self.controller.show_page(AccountView.__name__)
            else:
                self.fail_text.configure(text=reply)

        else:
            self.fail_text.configure(text="All fields marked * must be set, and must be properly formatted.")

    def delete_account(self):
        """Delete the account from the system. Verify this is intended first."""
        if self.current_account is not None:
            answer = tkmb.askyesno("Deleting Account.",
                                   "Are you sure you would like to delete this account "
                                   "and all data associated with it.")

            if answer:
                refund_amount = self.current_account.balance

                if refund_amount < 0:
                    tkmb.showinfo("Money owed.", f"The customer owes £{(refund_amount / 100) * -1}")
                else:
                    tkmb.showinfo("Refund.", f"The customer is owed £{(refund_amount / 100)}.")

                # Delete the account entry
                status, reply = SYSTEM.delete_account(self.current_account.account_id)

                if status:
                    self.controller.show_page(LandingPage.__name__)
                else:
                    tkmb.showerror("Account could not be deleted.", f"Reason: {reply}")
            else:
                tkmb.showinfo("Account deletion cancelled.", "The account has not been deleted.")

        else:
            tkmb.showerror("Account Error.", "Cannot delete account as no account is selected. Please try again.")

    def load_account_info(self):
        """Load the customer info onto the page"""
        if self.current_account is None:
            tkmb.showerror("Account Error.", "There was an error loading the account. No account has been selected.")

            self.account_id_lbl.configure(text="")
            self.account_num_lbl.configure(text="")
            self.balance_lbl.configure(text="")

            self.account_name_ent.delete(0, "end")

            self.overdraft_ent.delete(0, "end")

            self.interest_ent.delete(0, "end")
        else:
            self.account_id_lbl.configure(text=str(self.current_account.account_id))
            self.account_num_lbl.configure(text=str(self.current_account.account_num))
            self.balance_lbl.configure(text=f"£{self.current_account.balance/100}")

            self.account_name_ent.delete(0, "end")
            self.account_name_ent.insert(0, self.current_account.account_name)

            self.overdraft_ent.delete(0, "end")
            self.overdraft_ent.insert(0, str(self.current_account.overdraft_limit/100))

            self.interest_ent.delete(0, "end")
            self.interest_ent.insert(0, str(self.current_account.interest_rate))

    def set_account(self, account):
        """Sets the account to be updated"""
        self.current_account = account

    def page_update(self):
        """Runs when the page is shown"""
        self.load_account_info()

        self.fail_text.configure(text="")


class AccountView(PageBase):
    """View page for details about an account"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        self.current_account = None

        # Title
        header = tk.Frame(self)
        header.pack(side="top", pady=15)

        tk.Label(header, text="Account Information", font=FONTS["l"]).grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Update button
        tk.Button(header, text="Update Account", font=FONTS["m"],
                  command=self.update_account).grid(row=1, column=0, sticky="nsew", padx=25)

        # Transfer button
        tk.Button(header, text="Transfer Money", font=FONTS["m"],
                  command=self.go_to_transfer).grid(row=1, column=1, sticky="nsew")

        # Deposit/withdraw button
        tk.Button(header, text="Deposit/Withdraw", font=FONTS["m"],
                  command=self.go_to_deposit).grid(row=1, column=2)

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

        # Account Number
        tk.Label(data_frame, text="Account Number: ", font=FONTS["m"]).grid(row=1, column=0, sticky="w")
        self.account_num_label = tk.Label(data_frame, text="", font=FONTS["m"])
        self.account_num_label.grid(row=1, column=1, sticky="w")

        tk.Button(data_frame, text="Copy", font=FONTS["m"],
                  command=self.copy_acc_num).grid(row=1, column=2, sticky="nsew")

        # Account Balance
        tk.Label(data_frame, text="Balance: ", font=FONTS["m"]).grid(row=2, column=0, sticky="w")
        self.balance_lbl = tk.Label(data_frame, text="£-.--", font=FONTS["m"])
        self.balance_lbl.grid(row=2, column=1, sticky="w")

        # Account overdraft
        tk.Label(data_frame, text="Overdraft limit: ", font=FONTS["m"]).grid(row=3, column=0, sticky="w")
        self.overdraft_lbl = tk.Label(data_frame, text="£-.--", font=FONTS["m"])
        self.overdraft_lbl.grid(row=3, column=1, sticky="w")

        # Account interest rate
        tk.Label(data_frame, text="Interest rate: ", font=FONTS["m"]).grid(row=4, column=0, sticky="w")
        self.interest_lbl = tk.Label(data_frame, text="-.-%", font=FONTS["m"])
        self.interest_lbl.grid(row=4, column=1, sticky="w")

        # Account Holder
        tk.Label(data_frame, text="Account Holder: ", font=FONTS["m"]).grid(row=5, column=0, sticky="w")
        self.account_holder_lbl = tk.Label(data_frame, text="-.-%", font=FONTS["m"])
        self.account_holder_lbl.grid(row=5, column=1, sticky="w")

        self.customer_view_btn = tk.Button(data_frame, text="View Account", font=FONTS["m"])
        self.customer_view_btn.grid(row=5, column=2, sticky="nsew")

    def go_to_transfer(self):
        """Pre-fill the transfer page with this accounts data, then navigate there."""
        if self.current_account is None:
            tkmb.showerror("Issue setting field.", "No customer is currently selected.")
            return
        else:
            page = self.controller.Pages[AccountTransfer.__name__]
            page.set_from_input(str(self.current_account.account_num))

            self.controller.show_page(AccountTransfer.__name__)

    def go_to_deposit(self):
        """Pre-fill the deposit account number and then navigate there"""
        if self.current_account is None:
            tkmb.showerror("Issue setting field.", "No customer is currently selected.")
            return
        else:
            page = self.controller.Pages[AccountDepositWithdraw.__name__]
            page.fill_account_num(str(self.current_account.account_num))

            self.controller.show_page(AccountDepositWithdraw.__name__)

    def copy_acc_num(self):
        """Copies the current account number to clipboard"""
        if self.current_account is None:
            tkmb.showerror("Copy error.", "No account currently selected.")
        else:
            win.clipboard_clear()
            win.clipboard_append(self.current_account.account_num)
            win.update()

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
            self.account_num_label.configure(text=f"{account.account_num}")
            self.balance_lbl.configure(text=f"£{account.balance / 100}")
            self.overdraft_lbl.configure(text=f"£{account.overdraft_limit / 100}")
            self.interest_lbl.configure(text=f"{account.interest_rate}%")
            self.account_holder_lbl.configure(text=f"{account.customer.first_name} {account.customer.last_name}")
            self.customer_view_btn.configure(command=lambda: self.view_customer(account.customer.customer_id))

        self.current_account = account

    def view_customer(self, customer_id: int):
        """Opens the customer page and sets it up to view the customer with given id"""
        self.controller.Pages[CustomerView.__name__].load_customer_info(customer_id)
        self.controller.show_page(CustomerView.__name__)

    def update_account(self):
        """Send the user to the account update page"""
        if self.current_account is None:
            tkmb.showerror("Account Error." "No account is currently selected. Please go to Home and then try again.")
        else:
            self.controller.Pages[AccountUpdate.__name__].set_account(self.current_account)
            self.controller.show_page(AccountUpdate.__name__)


class AccountTransfer(PageBase):
    """Transfer money between accounts page"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        self.clear_from_field = True

        # Title
        tk.Label(self, text="Money Transfers", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Text shown on failure
        self.fail_text = tk.Label(self, text="",
                                  font=FONTS["s"], fg="#dd0000")
        self.fail_text.pack(side="top")

        # Input parent frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y", pady=30)

        from_frame = tk.LabelFrame(input_frame, text=" From ", font=FONTS["m"])
        from_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=20)

        to_frame = tk.LabelFrame(input_frame, text=" To ", font=FONTS["m"])
        to_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=20)

        row = 0

        # From and to accounts
        tk.Label(from_frame, text="Account Number", font=FONTS["m"]).grid(row=row, column=0, sticky="nsew")

        tk.Label(to_frame, text="Account Number", font=FONTS["m"]).grid(row=row, column=0, sticky="nsew")

        row += 1

        self.from_acc_num_ent = tk.Entry(from_frame, font=FONTS["m"], highlightbackground="#eeeeee",
                                         highlightcolor="#ffffff", highlightthickness=2)
        self.from_acc_num_ent.grid(row=row, column=0, sticky="nsew")

        # Bind key press and release to the check function
        self.from_acc_num_ent.bind("<KeyPress>", self.on_from_num_press)
        self.from_acc_num_ent.bind("<KeyRelease>", self.on_from_num_press)

        self.to_acc_num_ent = tk.Entry(to_frame, font=FONTS["m"], highlightbackground="#eeeeee",
                                       highlightcolor="#eeeeee", highlightthickness=2)
        self.to_acc_num_ent.grid(row=row, column=0, sticky="nsew")

        # Bind key press/release to the show function
        self.to_acc_num_ent.bind("<KeyPress>", self.on_to_num_press)
        self.to_acc_num_ent.bind("<KeyRelease>", self.on_to_num_press)

        row += 1

        self.from_name_lbl = tk.Label(from_frame, text="", font=FONTS["m"])
        self.from_name_lbl.grid(row=row, column=0, sticky="nsew")

        self.to_name_lbl = tk.Label(to_frame, text="", font=FONTS["m"])
        self.to_name_lbl.grid(row=row, column=0, sticky="nsew")

        # Amount
        tk.Label(input_frame, text="Amount to transfer: £", font=FONTS["m"]).grid(row=1, column=0, sticky="e", pady=30)

        self.amount_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.amount_ent.grid(row=1, column=1, sticky="nsew", pady=30)

        # Submit
        tk.Button(input_frame, text="Transfer", font=FONTS["m"],
                  command=self.submit).grid(row=2, column=0, columnspan=2, sticky="nsew")

    def submit(self):
        """Validates and runs the form."""
        from_num = self.from_acc_num_ent.get()
        to_num = self.to_acc_num_ent.get()
        amount = self.amount_ent.get()

        def check_int(inp: str, type=int):
            try:
                inp = type(inp)
                return True
            except:
                return False

        if check_int(from_num):
            from_num = int(from_num)
        else:
            self.fail_text.configure(text="All inputs must be a numbers.")
            return

        if check_int(to_num):
            to_num = int(to_num)
        else:
            self.fail_text.configure(text="All inputs must be a numbers.")
            return

        if check_int(amount, type=float):
            amount = float(amount)
            amount *= 100 # Convert from £s input to pence for storage
            amount = int(amount)
        else:
            self.fail_text.configure(text="All inputs must be a numbers.")
            return

        status, reply = SYSTEM.transfer(from_num, to_num, amount)
        if status:
            tkmb.showinfo("Money transfer successful.", "Successfully transferred money between the two accounts.")
        else:
            tkmb.showerror("Money transfer failed.", f"Could not transfer money between the accounts. Reason: {reply}")

    def set_from_input(self, account_num: int):
        """Update the account input field"""
        self.from_acc_num_ent.delete(0, "end")
        self.from_acc_num_ent.insert(0, str(account_num))

        # Change the flag so the from field is not wiped on page show
        self.clear_from_field = False

        # Manually trigger the information update event function
        self.on_from_num_press(None)

    def on_from_num_press(self, event):
        """Bound to on key down function of from acc num entry"""
        inp = self.from_acc_num_ent.get()

        if len(inp) == 0:
            self.from_name_lbl.configure(text="")
            self.from_acc_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
            return

        try:
            inp = int(inp)
            self.from_acc_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
        except:
            self.from_acc_num_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000")
            self.from_name_lbl.configure(text="Non integer input.")
            return

        accounts, reply = SYSTEM.search_accounts(account_number=inp)
        if len(accounts) == 0:
            self.from_name_lbl.configure(text="Account dont exist.")
        else:
            account = accounts[0]
            self.from_name_lbl.configure(text=account.account_name + "\n" +
                                         account.customer.first_name + " " + account.customer.last_name + "\n" +
                                         "£" + str(account.balance / 100))

    def on_to_num_press(self, event):
        """Bound to on key down function of to acc id entry"""
        inp = self.to_acc_num_ent.get()

        if len(inp) == 0:
            self.to_name_lbl.configure(text="")
            self.to_acc_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
            return

        try:
            inp = int(inp)
            self.to_acc_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
        except:
            self.to_acc_num_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000")
            self.to_name_lbl.configure(text="Non integer input.")
            return

        accounts, reply = SYSTEM.search_accounts(account_number=inp)
        if len(accounts) == 0:
            self.to_name_lbl.configure(text="Account dont exist.")
        else:
            account = accounts[0]
            self.to_name_lbl.configure(text=account.account_name + "\n" +
                                       account.customer.first_name + " " + account.customer.last_name)

    def page_update(self):
        """Runs on page update"""
        self.to_acc_num_ent.delete(0, "end")
        self.amount_ent.delete(0, "end")

        # Clear from field or reset flag
        if self.clear_from_field:
            self.from_acc_num_ent.delete(0, "end")
        else:
            # reset the flag
            self.clear_from_field = True

        # Trigger the key events for the information, manually
        self.on_from_num_press(None)
        self.on_to_num_press(None)


class AccountDepositWithdraw(PageBase):
    """Deposit and withdraw page"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Flags whether or not to clear the account number
        self.clear_acc_num = True

        # Title
        tk.Label(self, text="Deposit or withdraw", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Text shown on failure
        self.fail_text = tk.Label(self, text="",
                                  font=FONTS["s"], fg="#dd0000")
        self.fail_text.pack(side="top")

        # Input parent frame
        input_frame = tk.Frame(self)
        input_frame.pack(side="top", fill="y", pady=30)

        row = 0

        # Account Number
        tk.Label(input_frame, text="Account Number: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nsew")

        self.account_num_ent = tk.Entry(input_frame, font=FONTS["m"], highlightbackground="#eeeeee",
                                        highlightcolor="#eeeeee", highlightthickness=2)
        self.account_num_ent.grid(row=row, column=1, sticky="nsew")

        self.account_num_ent.bind("<KeyPress>", self.on_acc_num_press)
        self.account_num_ent.bind("<KeyRelease>", self.on_acc_num_press)

        row += 1

        self.account_name_lbl = tk.Label(input_frame, text="", font=FONTS["m"])
        self.account_name_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        self.account_holder_lbl = tk.Label(input_frame, text="", font=FONTS["m"])
        self.account_holder_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        self.account_balance_lbl = tk.Label(input_frame, text="", font=FONTS["m"])
        self.account_balance_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        self.account_overdraft_lbl = tk.Label(input_frame, text="", font=FONTS["m"])
        self.account_overdraft_lbl.grid(row=row, column=1, sticky="w")

        row += 1

        ttk.Separator(input_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="nsew")

        row += 1

        # Transfer or deposit
        self.option = tk.IntVar()

        tk.Radiobutton(input_frame, variable=self.option, value=0,
                       text="Deposit", font=FONTS["m"]).grid(row=row, column=0, sticky="w")

        tk.Radiobutton(input_frame, variable=self.option, value=1,
                       text="Withdraw", font=FONTS["m"]).grid(row=row, column=1, sticky="w")

        row += 1

        # Amount
        tk.Label(input_frame, text="Amount: £", font=FONTS["m"]).grid(row=row, column=0, sticky="e")

        self.amount_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.amount_ent.grid(row=row, column=1, sticky="nsew")

        row += 1

        # Submit button
        tk.Button(input_frame, text="Update", font=FONTS["m"], bg="#00dd00",
                  command=self.submit).grid(row=row, column=0, columnspan=2, sticky="nsew", pady=30, padx=5)

    def on_acc_num_press(self, event):
        """Bound to on key down function of from acc num entry"""
        inp = self.account_num_ent.get()

        if len(inp) == 0:
            self.account_name_lbl.configure(text="")
            self.account_holder_lbl.configure(text="")
            self.account_balance_lbl.configure(text="")
            self.account_overdraft_lbl.configure(text="")
            self.account_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
            return

        # Convert to int or return
        try:
            inp = int(inp)
            self.account_num_ent.configure(highlightbackground="#eeeeee", highlightcolor="#eeeeee")
        except:
            self.account_num_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000")
            self.account_name_lbl.configure(text="Non integer input.")
            self.account_holder_lbl.configure(text="")
            self.account_balance_lbl.configure(text="")
            self.account_overdraft_lbl.configure(text="")
            return

        accounts, reply = SYSTEM.search_accounts(account_number=inp)
        if len(accounts) == 0:
            self.account_name_lbl.configure(text="Account dont exist.")
            self.account_holder_lbl.configure(text="")
            self.account_balance_lbl.configure(text="")
            self.account_overdraft_lbl.configure(text="")
        else:
            account = accounts[0]
            self.account_name_lbl.configure(text=account.account_name)
            self.account_holder_lbl.configure(text=account.customer.first_name + account.customer.last_name)
            self.account_balance_lbl.configure(text=f"Balance: £{account.balance / 100}")
            self.account_overdraft_lbl.configure(text=f"Overdraft: £{account.overdraft_limit / 100}")

    def fill_account_num(self, account_num):
        """Pre fill the account number"""
        self.account_num_ent.delete(0, "end")
        self.account_num_ent.insert(0, str(account_num))

        # Set the flag so that this information is not wiped on page show
        self.clear_acc_num = False

        # Manual trigger on key press event to update info
        self.on_acc_num_press(None)

    def submit(self):
        """Submit the form"""
        acc_num = self.account_num_ent.get()
        option = self.option.get()
        amount = self.amount_ent.get()

        # Convert account number to integer
        try:
            acc_num = int(acc_num)
        except:
            self.fail_text.configure(text="Account number must be an integer.")
            return

        # Convert amount into integer of pence
        try:
            amount = float(amount)
            amount *= 100
            amount = int(amount)
        except:
            self.fail_text.configure(text="Amount must be a number.")
            return

        # Get account id from number
        accounts, reply = SYSTEM.search_accounts(account_number=acc_num)

        if len(accounts) == 0:
            self.fail_text.configure(text="That account does not exist.")
            return

        account = accounts[0]

        # Check chosen method and run that
        if option == 0:
            # Deposit
            stat, reply = SYSTEM.deposit(account.account_id, amount)

            if stat:
                tkmb.showinfo("Deposit Successful.", "Deposit successfully completed.")
            else:
                tkmb.showerror("Deposit Failed", f"Deposit failed due to the following: {reply}")
        else:
            # Withdraw
            stat, reply = SYSTEM.withdraw(account.account_id, amount)

            if stat:
                tkmb.showinfo("Withdraw Successful.", "Withdrawal successfully completed.")
            else:
                tkmb.showerror("Withdraw Failed", f"Deposit failed due to the following: {reply}")

        # Manual event trigger on account num key press event to update information
        self.on_acc_num_press(None)

    def page_update(self):
        """Runs when this page is shown"""
        # Clear fields
        self.amount_ent.delete(0, "end")

        self.option.set(0)

        # Check the flag and reset it if its off
        if self.clear_acc_num:
            self.account_num_ent.delete(0, "end")
        else:
            self.clear_acc_num = True

        # Manually trigger information show event
        self.on_acc_num_press(None)


class AdminView(PageBase):
    """View details about the current admin account"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # title
        tk.Label(self, text="Your account", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Update button
        tk.Button(self, text="Update Account", font=FONTS["m"],
                  command=lambda: controller.show_page(AdminUpdate.__name__)).pack(side="top", pady=5)

        data_frame = tk.Frame(self)
        data_frame.pack(side="top", pady=10)


        row = 0

        # Name
        tk.Label(data_frame, text="Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")

        self.name_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.name_lbl.grid(row=row, column=1, sticky="nsw")

        row += 1

        # Username
        tk.Label(data_frame, text="Username: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")

        self.username_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.username_lbl.grid(row=row, column=1, sticky="nsw")

        row += 1

        # Address:
        tk.Label(data_frame, text="Address: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")

        self.addr_l1 = tk.Label(data_frame, text="", font=FONTS["m"])
        self.addr_l1.grid(row=row, column=1, sticky="nsw")

        row += 1

        self.addr_l2 = tk.Label(data_frame, text="", font=FONTS["m"])
        self.addr_l2.grid(row=row, column=1, sticky="nsw")

        row += 1

        self.addr_l3 = tk.Label(data_frame, text="", font=FONTS["m"])
        self.addr_l3.grid(row=row, column=1, sticky="nsw")

        row += 1

        self.addr_city = tk.Label(data_frame, text="", font=FONTS["m"])
        self.addr_city.grid(row=row, column=1, sticky="nsw")

        row += 1

        self.addr_post = tk.Label(data_frame, text="", font=FONTS["m"])
        self.addr_post.grid(row=row, column=1, sticky="nsw")

        row += 1
        row += 1

        # Rights
        tk.Label(data_frame, text="Full access rights: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")

        self.rights_lbl = tk.Label(data_frame, text="", font=FONTS["m"])
        self.rights_lbl.grid(row=row, column=1, sticky="nsw")

        # Log out button
        tk.Button(self, text="Log out", font=FONTS["m"], bg="#dd0000", width=10,
                  command=self.logout).pack(side="bottom", pady=20)

    def load_data (self):
        """Loads the data onto the page"""

        if SYSTEM.logged_in:
            self.name_lbl.configure(text=f"{SYSTEM.admin.first_name} {SYSTEM.admin.last_name}")
            self.username_lbl.configure(text=f"{SYSTEM.admin.get_username()}")
            self.addr_l1.configure(text=f"{SYSTEM.admin.get_address()[0]}")
            self.addr_l2.configure(text=f"{SYSTEM.admin.get_address()[1]}")
            self.addr_l3.configure(text=f"{SYSTEM.admin.get_address()[2]}")
            self.addr_city.configure(text=f"{SYSTEM.admin.get_address()[3]}")
            self.addr_post.configure(text=f"{SYSTEM.admin.get_address()[4]}")

            if SYSTEM.admin.full_rights:
                self.rights_lbl.configure(text="True", fg="#00dd00")
            else:
                self.rights_lbl.configure(text="False", fg="#dd0000")
        else:
            tkmb.showerror("An error has occured.", "No admin appears to be logged in. Returning to log in screen.")

            # Run the log out function just to clear everything up in-case of errors.
            SYSTEM.log_out()
            self.controller.show_page(LoginPage.__name__)

    def logout(self):
        """Logs the user out and returns to the home page"""
        SYSTEM.log_out()
        self.controller.show_page(LoginPage.__name__)

    def page_update(self):
        """Runs when the page is shown"""
        # Load the admin data
        self.load_data()


class AdminUpdate(PageBase):
    """Page for updating an admins information"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Admin Account Update.", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        # Required fields notice
        tk.Label(self, text="All fields with * are to be filled.",
                 font=FONTS["s"], fg="#dd0000").pack(side="top")

        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="x")

        input_frame = tk.Frame(self)
        input_frame.pack(side="top", pady=10)

        row = 0

        # Name Section
        tk.Label(input_frame, text="First *", font=FONTS["m"]).grid(row=row, column=1, sticky="nsew")

        tk.Label(input_frame, text="Last *", font=FONTS["m"]).grid(row=row, column=2, sticky="nsew")

        row += 1

        tk.Label(input_frame, text="Name: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse", pady=10)

        self.first_name_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.first_name_ent.grid(row=row, column=1, sticky="nsew", pady=10)

        self.last_name_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.last_name_ent.grid(row=row, column=2, sticky="nsew", padx=5, pady=10)

        row += 1

        # Username
        tk.Label(input_frame, text="Username: *", font=FONTS["m"]).grid(row=row, column=0, sticky="nse", pady=10)

        self.username_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.username_ent.grid(row=row, column=1, columnspan=2, sticky="nsew", pady=10)

        row += 1

        # Address
        tk.Label(input_frame, text="Address: *", font=FONTS["m"]).grid(row=row, column=0, sticky="nse", pady=10)

        self.addr_l1_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l1_ent.grid(row=row, column=1, columnspan=2, sticky="nsew", pady=10)

        row += 1

        self.addr_l2_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l2_ent.grid(row=row, column=1, columnspan=2, sticky="nsew", pady=10)

        row += 1

        self.addr_l3_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_l3_ent.grid(row=row, column=1, columnspan=2, sticky="nsew", pady=10)

        row += 1

        tk.Label(input_frame, text="City *", font=FONTS["m"]).grid(row=row, column=1, sticky="nsew")

        tk.Label(input_frame, text="Post code *", font=FONTS["m"]).grid(row=row, column=2, sticky="nsew")

        row += 1

        self.addr_city_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_city_ent.grid(row=row, column=1, sticky="nsew", pady=10)

        self.addr_post_ent = tk.Entry(input_frame, font=FONTS["m"])
        self.addr_post_ent.grid(row=row, column=2, sticky="nsew", pady=10, padx=5)

        row += 1

        # Submit
        tk.Button(input_frame, text="Update", font=FONTS["m"], bg="#00dd00",
                  command=self.submit).grid(row=row, column=1, columnspan=2, sticky="nsew")
        row += 1

        # Password Change Button
        tk.Button(input_frame, text="Update password", font=FONTS["m"], bg="#77aafc",
                  command=lambda: controller.show_page(AdminPasswordChange.__name__)).grid(row=row, column=1,
                                                                                           columnspan=2, sticky="nsew")

    def submit(self):
        """Validate and submit the form"""

        fname = self.first_name_ent.get()
        lname = self.last_name_ent.get()

        username = self.username_ent.get()

        addr_l1 = self.addr_l1_ent.get()
        addr_l2 = self.addr_l2_ent.get()
        addr_l3 = self.addr_l3_ent.get()
        addr_city = self.addr_city_ent.get()
        addr_post = self.addr_post_ent.get()

        def verify_data(inp):
            """Verifies that there is actually data provided rather than an emtpy input field"""
            if len(inp) > 0:
                return True
            else:
                return False

        run = True
        kwargs = {}

        if not verify_data(fname):
            run = False
            self.first_name_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.first_name_ent.configure(highlightthickness=0)
            kwargs["first_name"] = fname

        if not verify_data(lname):
            run = False
            self.last_name_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.last_name_ent.configure(highlightthickness=0)
            kwargs["last_name"] = lname

        if not verify_data(username):
            run = False
            self.username_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.username_ent.configure(highlightthickness=0)
            kwargs["username"] = username

        if not verify_data(addr_l1):
            run = False
            self.addr_l1_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_l1_ent.configure(highlightthickness=0)
            kwargs["addr_l1"] = addr_l1

        if not verify_data(addr_city):
            run = False
            self.addr_city_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_city_ent.configure(highlightthickness=0)
            kwargs["addr_city"] = addr_city

        if not verify_data(addr_post):
            run = False
            self.addr_post_ent.configure(highlightbackground="#dd0000", highlightcolor="#dd0000", highlightthickness=2)
        else:
            self.addr_post_ent.configure(highlightthickness=0)
            kwargs["addr_post"] = addr_post

        # Non required fields
        kwargs["addr_l2"] = addr_l2
        kwargs["addr_l3"] = addr_l3

        if run:
            status, reply, admin = SYSTEM.update_admin(SYSTEM.admin.admin_id, **kwargs)

            if status:
                SYSTEM.admin = admin

                tkmb.showinfo("Success.", "Successfully updated the admin information.")
                self.controller.show_page(AdminView.__name__)
            else:
                self.fail_text.configure(text=reply)

        else:
            self.fail_text.configure(text="All required fields must be filled.")

    def load_data(self):
        """Load the admin data into the entry fields"""

        # Clear the fields
        self.first_name_ent.delete(0, "end")
        self.last_name_ent.delete(0, "end")
        self.username_ent.delete(0, "end")
        self.addr_l1_ent.delete(0, "end")
        self.addr_l2_ent.delete(0, "end")
        self.addr_l3_ent.delete(0, "end")
        self.addr_city_ent.delete(0, "end")
        self.addr_post_ent.delete(0, "end")

        # Insert data
        self.first_name_ent.insert(0, str(SYSTEM.admin.first_name))
        self.last_name_ent.insert(0, str(SYSTEM.admin.last_name))
        self.username_ent.insert(0, str(SYSTEM.admin.username))
        self.addr_l1_ent.insert(0, str(SYSTEM.admin.address[0]))
        if SYSTEM.admin.address[1] is not None:
            self.addr_l2_ent.insert(0, str(SYSTEM.admin.address[1]))
        if SYSTEM.admin.address[2]:
            self.addr_l3_ent.insert(0, str(SYSTEM.admin.address[2]))
        self.addr_city_ent.insert(0, str(SYSTEM.admin.address[3]))
        self.addr_post_ent.insert(0, str(SYSTEM.admin.address[4]))

    def page_update(self):
        """Runs when the page is shown"""
        # Load new data onto page
        self.load_data()


class AdminPasswordChange(PageBase):
    """Page for admins to change their password"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Password Change", font=FONTS["l"]).pack(side="top", fill="x", pady=5)

        self.fail_text = tk.Label(self, text="", font=FONTS["m"], fg="#dd0000")
        self.fail_text.pack(side="top", fill="x")

        input_frame = tk.Frame(self)
        input_frame.pack(side="top", pady=10)

        # Old Password
        tk.Label(input_frame, text="Current Password: ", font=FONTS["m"]).grid(row=0, column=0, sticky="nse", pady=5)

        self.old_pass_ent = tk.Entry(input_frame, show="*", font=FONTS["m"])
        self.old_pass_ent.grid(row=0, column=1, sticky="nsew", pady=5)

        # New Password
        tk.Label(input_frame, text="New Password: ", font=FONTS["m"]).grid(row=1, column=0, sticky="nse", pady=5)

        self.new_pass_ent = tk.Entry(input_frame, show="*", font=FONTS["m"])
        self.new_pass_ent.grid(row=1, column=1, sticky="nsew", pady=5)

        # Confirm Password
        tk.Label(input_frame, text="Confirm Password: ", font=FONTS["m"]).grid(row=2, column=0, sticky="nse", pady=5)

        self.conf_pass_ent = tk.Entry(input_frame, show="*", font=FONTS["m"])
        self.conf_pass_ent.grid(row=2, column=1, sticky="nsew", pady=5)

        # Submit
        tk.Button(input_frame, text="Update Password", font=FONTS["m"], bg="#00dd00",
                  command=self.update_password).grid(row=3, column=0, columnspan=2, sticky="nsew")

    def update_password(self):
        """Submits the data to the BankSystem to verify"""
        old = self.old_pass_ent.get()
        new = self.new_pass_ent.get()
        conf = self.conf_pass_ent.get()

        if len(new) < 8:
            self.fail_text.configure(text="New password must be 8 characters or longer.")
            return

        stat, reply = SYSTEM.update_admin_password(old, new, conf)

        if stat:
            tkmb.showinfo("Success", "Password updated successfully.")
            self.controller.show_page(AdminView.__name__)
        else:
            self.fail_text.configure(text=reply)

    def page_update(self):
        """Runs when the page is shown"""
        # Clear fields
        self.old_pass_ent.delete(0, "end")
        self.new_pass_ent.delete(0, "end")
        self.conf_pass_ent.delete(0, "end")

        # Clear fail text
        self.fail_text.configure(text="")


class ReportAll(PageBase):
    """A page that shows all the reports"""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        create_navigation_bar(self, controller)

        # Title
        tk.Label(self, text="Full management report", font=FONTS["l"]).pack(side="top", fill="x", pady=10)

        data_frame = tk.Frame(self)
        data_frame.pack(side="top", pady=10)

        interest_frame = tk.Frame(data_frame)
        interest_frame.grid(row=0, column=0, sticky="nsew")

        row = 0

        # Interest
        tk.Label(interest_frame, text="Interest Report", font=FONTS["l"]).grid(row=row, column=0,
                                                                           columnspan=3, sticky="nsew")

        row += 1

        #   Accounts
        tk.Label(interest_frame, text="Accounts: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.interest_accounts = tk.Label(interest_frame, text="", font=FONTS["m"])
        self.interest_accounts.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Total
        tk.Label(interest_frame, text="Total Interest (1 year): ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.interest_total = tk.Label(interest_frame, text="", font=FONTS["m"])
        self.interest_total.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Mean
        tk.Label(interest_frame, text="Mean interest rate: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.interest_mean = tk.Label(interest_frame, text="", font=FONTS["m"])
        self.interest_mean.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Highest
        tk.Label(interest_frame, text="Highest interest: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.interest_highest = tk.Label(interest_frame, text="", font=FONTS["m"])
        self.interest_highest.grid(row=row, column=1, sticky="nsw")

        self.interest_high_button = tk.Button(interest_frame, text="View Account", font=FONTS["m"])
        self.interest_high_button.grid(row=row, column=2, sticky="nsew")

        row += 1

        #   Lowest
        tk.Label(interest_frame, text="Lowest interest: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.interest_lowest = tk.Label(interest_frame, text="", font=FONTS["m"])
        self.interest_lowest.grid(row=row, column=1, sticky="nsw")

        self.interest_low_button = tk.Button(interest_frame, text="View Account", font=FONTS["m"])
        self.interest_low_button.grid(row=row, column=2, sticky="nsew")

        # Separate
        ttk.Separator(data_frame, orient="vertical").grid(row=0, column=1, sticky="nsew", padx=5)


        # Balance
        balance_frame = tk.Frame(data_frame)
        balance_frame.grid(row=0, column=2, sticky="nsew")

        row = 0

        tk.Label(balance_frame, text="Balance Report", font=FONTS["l"]).grid(row=row, column=0,
                                                                             columnspan=3, sticky="nsew")

        row += 1

        #   Accounts
        tk.Label(balance_frame, text="Accounts: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.balance_accounts = tk.Label(balance_frame, text="", font=FONTS["m"])
        self.balance_accounts.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Total
        tk.Label(balance_frame, text="Total balances: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.balance_total = tk.Label(balance_frame, text="", font=FONTS["m"])
        self.balance_total.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Mean
        tk.Label(balance_frame, text="Mean balance: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.balance_mean = tk.Label(balance_frame, text="", font=FONTS["m"])
        self.balance_mean.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Highest
        tk.Label(balance_frame, text="Highest balance: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.balance_highest = tk.Label(balance_frame, text="", font=FONTS["m"])
        self.balance_highest.grid(row=row, column=1, sticky="nsw")

        self.balance_high_button = tk.Button(balance_frame, text="View Account", font=FONTS["m"])
        self.balance_high_button.grid(row=row, column=2, sticky="nsew")

        row += 1

        #   Lowest
        tk.Label(balance_frame, text="Lowest balance: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.balance_lowest = tk.Label(balance_frame, text="", font=FONTS["m"])
        self.balance_lowest.grid(row=row, column=1, sticky="nsw")

        self.balance_low_button = tk.Button(balance_frame, text="View Account", font=FONTS["m"])
        self.balance_low_button.grid(row=row, column=2, sticky="nsew")

        # Separate
        ttk.Separator(data_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)

        # Overdraft
        overdraft_frame = tk.Frame(data_frame)
        overdraft_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

        row = 0

        # Title
        tk.Label(overdraft_frame, text="Overdraft Report", font=FONTS["l"]).grid(row=row, column=0,
                                                                                 columnspan=3, sticky="nsew")

        row += 1

        #   Accounts
        tk.Label(overdraft_frame, text="Accounts: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.overdraft_accounts = tk.Label(overdraft_frame, text="", font=FONTS["m"])
        self.overdraft_accounts.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Total
        tk.Label(overdraft_frame, text="Total Overdrafts: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.overdraft_total = tk.Label(overdraft_frame, text="", font=FONTS["m"])
        self.overdraft_total.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Mean
        tk.Label(overdraft_frame, text="Mean overdrafts: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.overdraft_mean = tk.Label(overdraft_frame, text="", font=FONTS["m"])
        self.overdraft_mean.grid(row=row, column=1, sticky="nsw")

        row += 1

        #   Highest
        tk.Label(overdraft_frame, text="Highest overdraft: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.overdraft_highest = tk.Label(overdraft_frame, text="", font=FONTS["m"])
        self.overdraft_highest.grid(row=row, column=1, sticky="nsw")

        self.overdraft_high_button = tk.Button(overdraft_frame, text="View Account", font=FONTS["m"])
        self.overdraft_high_button.grid(row=row, column=2, sticky="nsew")

        row += 1

        #   Lowest
        tk.Label(overdraft_frame, text="Lowest overdraft: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")
        self.overdraft_lowest = tk.Label(overdraft_frame, text="", font=FONTS["m"])
        self.overdraft_lowest.grid(row=row, column=1, sticky="nsw")

        self.overdraft_low_button = tk.Button(overdraft_frame, text="View Account", font=FONTS["m"])
        self.overdraft_low_button.grid(row=row, column=2, sticky="nsew")

        # Separator
        ttk.Separator(data_frame, orient="vertical").grid(row=2, column=1, sticky="nsew", padx=5)

        # Customers report
        customers_frame = tk.Frame(data_frame)
        customers_frame.grid(row=2, column=2, sticky="nsew")

        row = 0

        # title
        tk.Label(customers_frame, text="Customers Report", font=FONTS["l"]).grid(row=row, column=0,
                                                                                 columnspan=2, sticky="nsew")

        row += 1

        # Customer total
        tk.Label(customers_frame, text="Customers: ", font=FONTS["m"]).grid(row=row, column=0, sticky="nse")

        self.customers = tk.Label(customers_frame, text="", font=FONTS["m"])
        self.customers.grid(row=row, column=1)

    def load_interest(self):
        """Get interest report, then populate data fields"""
        data = SYSTEM.interest_report()

        self.interest_accounts.configure(text=str(data["accounts_pop"]))
        self.interest_total.configure(text=str(round(data["interest_gained"] / 100, 2)))
        self.interest_mean.configure(text=str(round(data["mean"], 2)))

        self.interest_highest.configure(text=str(data["highest"].interest_rate) + "%")
        self.interest_high_button.configure(command=lambda hid=data["highest"].account_id: self.show_account(hid))

        self.interest_lowest.configure(text=str(data["lowest"].interest_rate) + "%")
        self.interest_low_button.configure(command=lambda lid=data["lowest"].account_id: self.show_account(lid))

    def load_balance(self):
        """Get interest report, then populate data fields"""
        data = SYSTEM.balance_report()

        self.balance_accounts.configure(text=str(data["accounts_pop"]))
        self.balance_total.configure(text="£" + str(round(data["total"] / 100, 2)))
        self.balance_mean.configure(text="£" + str(round(data["mean"] / 100, 2)))

        self.balance_highest.configure(text="£" + str(data["highest"].balance / 100))
        self.balance_high_button.configure(command=lambda hid=data["highest"].account_id: self.show_account(hid))

        self.balance_lowest.configure(text="£" + str(data["lowest"].balance / 100))
        self.balance_low_button.configure(command=lambda lid=data["lowest"].account_id: self.show_account(lid))

    def load_overdraft(self):
        """Load the overdraft data in"""
        data = SYSTEM.overdraft_report()

        self.overdraft_accounts.configure(text=str(data["accounts_pop"]))
        self.overdraft_total.configure(text="£" + str(round(data["total"] / 100, 2)))
        self.overdraft_mean.configure(text="£" + str(round(data["mean"] / 100, 2)))

        self.overdraft_highest.configure(text="£" + str(data["highest"].overdraft_limit / 100))
        self.overdraft_high_button.configure(command=lambda hid=data["highest"].account_id: self.show_account(hid))

        self.overdraft_lowest.configure(text="£" + str(data["lowest"].overdraft_limit / 100))
        self.overdraft_low_button.configure(command=lambda lid=data["lowest"].account_id: self.show_account(lid))

    def load_customers(self):
        """Get the customers report and load the data onto the page"""
        data = SYSTEM.customer_report()

        self.customers.configure(text=str(data["customers_pop"]))

    def show_account(self, accid):
        """Shows the account page with the given user loaded"""
        self.controller.Pages[AccountView.__name__].load_account_info(accid)
        self.controller.show_page(AccountView.__name__)

    def page_update(self):
        """Runs everytime the page is opened"""
        self.load_interest()
        self.load_balance()
        self.load_overdraft()
        self.load_customers()




# TODO: If time permits, add all the customers accounts as a pre-fill options in the transfer page

# TODO: Alter the rights restrictions on certain functions, cross reference this with moodle docs
# TODO: GUI tweaks.


if __name__ == "__main__":
    win = Window()
    win.mainloop()
