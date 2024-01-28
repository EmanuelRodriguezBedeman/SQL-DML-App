# Imports
import customtkinter # GUI
import mysql.connector # MySQL
from collections import defaultdict # Creates Dict
from itertools import zip_longest # Fills empty dict values
from functools import partial

customtkinter.set_appearance_mode("system")  # default

# Block to get the tables names and their columns
try:
    with mysql.connector.connect(
        user='root',
        password='password',
        host='127.0.0.1',
        database='girrafe'
    ) as cnx:
        cursor = cnx.cursor(buffered=True)

        # Get All the tables names
        tables_query = ("SHOW TABLES;")

        # Execute query
        cursor.execute(tables_query)

        # Saves the table's names
        tables_names = [table[0] for table in cursor]

        # Empty dict with empty lists values
        tables_columns = defaultdict(list)

        # Loop to save the tables names and it's columns
        for name in tables_names:
            
            # Query for each table's columns
            query = (
                f"""
                SELECT `COLUMN_NAME`
                FROM `INFORMATION_SCHEMA`.`COLUMNS`
                WHERE `TABLE_NAME` = %s;
                """
            )

            # Executes the query
            cursor.execute(query, [name])

            # Obtains all the rows from the query
            columns = cursor.fetchall()

            # Dict with tables names and their columns
            tables_columns[name].extend(columns[0] for columns in columns)

except mysql.connector.Error as err:
    print(f"Error: {err}")

# --------------------------------- Application -----------------------------------------

# Message Window
class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(self, text="ToplevelWindow")
        self.label.pack(padx=20, pady=20)

# Tables Frame
class TablesFrame(customtkinter.CTkFrame):
    def __init__(self, master, tables):
        super().__init__(master)

        # Buttons attributes
        self.tables = tables

        def optionmenu_callback(choice):
            print("Dropdown:", choice)

        label = customtkinter.CTkLabel(self, text="Choose table:", fg_color="transparent")
        label.grid(row=0, column=0, padx=20, pady=20)
        optionmenu = customtkinter.CTkOptionMenu(self, values=tables, command=optionmenu_callback)
        optionmenu.grid(row=0, column=1, padx=20, pady=20)

# Entries Frame
class EntryFrames(customtkinter.CTkFrame):
    def __init__(self, master, labels):
        super().__init__(master)

        # Objects attributes
        self.labels = labels
        self.entries = []

        # Create entries Dynamically
        for i, label in enumerate(labels):
            label = customtkinter.CTkLabel(self, text=label, fg_color="transparent")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, width=180)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.entries.append(entry)

    # Obtains entries values
    def get(self):
        entries_content = []
        for entry in self.entries:
            if entry.get() != "":
                entries_content.append(entry.get())
        return entries_content

    def read(self):
        pass

    def clear(self):
        for entry in self.entries:
            entry.delete(0, len(entry.get()))

# CRUD Buttons Frame
class CrudFrame(customtkinter.CTkFrame):
    def __init__(self, master, texts, entries):
        super().__init__(master)

        # Buttons attributes
        self.texts = texts
        self.entries = entries

        # Message Window Default value
        self.msg_window = None

        # Create Message Window
        def open_msg_window(self):
            if self.msg_window is None or not self.msg_window.winfo_exists():
                self.msg_window = MessageWindow(self)  # create window if its None or destroyed
            else:
                print("else")
                self.msg_window.focus()  # if window exists focus it

        def create():
            print("Created!")

        def read():
                print(self.entries.get())

        def update():
            print("Updated!")

        def delete():
            print("Deleted!")

        def clear():
            self.entries.clear()
            open_msg_window(self)

        functions = [create, read, update, delete]

        for i, (text, function) in enumerate(zip(self.texts, functions)):
            button = customtkinter.CTkButton(self, width=0.5, text=text, command=function)
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        clear_button = customtkinter.CTkButton(self, text="Clear Fields", command=clear)
        clear_button.grid(row=1, columnspan=len(self.texts), padx=10, pady=10, sticky="ew")

# Application Class
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_default_color_theme("blue")
        self.title("SQL DML App")
        # self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tables Frame
        self.tables = TablesFrame(self, tables=list(tables_columns.keys()))
        self.tables.grid(row=0, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Fields Frame
        self.fields = EntryFrames(self, labels=["ID", "Name", "Lastname", "Adress", "Password", "Notes"])
        self.fields.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Buttons Frame
        self.crud_buttons = CrudFrame(self, texts=["Create", "Read", "Update", "Delete"], entries=self.fields)
        self.crud_buttons.grid(row=2, column=0, padx=20, pady=(0,20), sticky="nsew")

        self.toplevel_window = None

        def open_toplevel(self):
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = MessageWindow(self)  # create window if its None or destroyed
            else:
                self.toplevel_window.focus()  # if window exists focus it
                
        self.button_2 = customtkinter.CTkButton(self, text="open toplevel", command=open_toplevel)
        self.button_2.grid(row=3, column=0, padx=20, pady=(0,20), sticky="nsew")

app = App()
app.mainloop()