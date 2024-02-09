# Imports
import customtkinter # GUI
import mysql.connector # MySQL
from collections import defaultdict # Creates Dict

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

# Input Dialogs
class Dialog(customtkinter.CTkInputDialog):
    def __init__(self, master, text, title):
        super().__init__(text=text, title=title)
        self.entry = self.get_input()

    def get_entry(self):
        return self.entry

# Message Window
class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self, master, text):
        super().__init__()
        self.title("Information")
        self.geometry("250x150")
        self.text = text

        self.label = customtkinter.CTkLabel(self, text=text)
        # self.label.pack(padx=20, pady=20)
        self.label.place(relx = 0.5, rely = 0.5, anchor="center")

# Tables Frame
class TablesFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Dropdown callback function
        def selected_table(table):
            # Sets entries to selected table's columns
            master.change_entries(table)

        label = customtkinter.CTkLabel(self, text="Choose table:", fg_color="transparent")
        label.grid(row=0, column=0, padx=20, pady=20)

        optionmenu = customtkinter.CTkOptionMenu(self, values=master.get_tables(), command=selected_table)
        optionmenu.grid(row=0, column=1, padx=20, pady=20)

# Entries Frame
class EntryFrames(customtkinter.CTkFrame):
    def __init__(self, master, labels):
        super().__init__(master)

        # Objects attributes
        self.labels = labels
        self.entries = []

        # Creates table's columns labels & entries
        for i, label in enumerate(labels):
            label = customtkinter.CTkLabel(self, text=label, fg_color="transparent")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, width=180)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.entries.append(entry)

    # Obtains entries values
    def get(self):
        entries_content = {}
        for label, entry in zip(self.labels, self.entries):
            entries_content[label] = entry.get()
        return entries_content

    def clear(self):
        for entry in self.entries:
            entry.delete(0, len(entry.get()))

# CRUD Buttons Frame
class CrudFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Buttons attributes
        self.texts = ["Create", "Read", "Update", "Delete"]

        # Message Window Default value
        self.msg_window = None

        # Create Message Window
        def open_msg_window(self, text):
            if self.msg_window is None or not self.msg_window.winfo_exists():
                self.msg_window = MessageWindow(self, text=text)  # create window if its None or destroyed
                self.msg_window.after(100, self.msg_window.lift)
                self.msg_window.resizable(False, False)
            else:
                print("else")
                self.msg_window.focus()  # if window exists focus it

        # Create button function
        def create_entry():
            print(master.create_entry())
            # open_msg_window(self, text="Data Created!")

        # Read button function
        def read_entry():
            print(master.read_entry())

        # Update button function
        def update_entry():
            print(master.update_entry())
            # open_msg_window(self, text="Data Updated!")

        # Delete button function
        def delete_entry():
            print(master.delete_entry())
            # open_msg_window(self, text="Data Deleted!")

        # Clear button function
        def clear_entries():
            # self.entries.clear()
            print(master.clear_entries())
            # open_msg_window(self, text="Fields Cleared!")

        functions = [create_entry, read_entry, update_entry, delete_entry]

        for i, (text, function) in enumerate(zip(self.texts, functions)):
            button = customtkinter.CTkButton(self, width=0.5, text=text, command=function)
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        clear_button = customtkinter.CTkButton(self, text="Clear Fields", command=clear_entries)
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

        # Input Dialogs
        # user = Dialog(self, text="Enter user:", title="MySQL User").get_entry()
        # password = Dialog(self, text="Enter password:", title="MySQL Password").get_entry()

        # print(user, password)

        # Tables and its columns
        self.tables_columns = tables_columns

        # Tables Frame
        self.tables = TablesFrame(self)
        self.tables.grid(row=0, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Fields Frame
        self.fields = EntryFrames(self, labels=self.get_columns(self.tables.selected_table))
        self.fields.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Buttons Frame
        self.crud_buttons = CrudFrame(self)
        self.crud_buttons.grid(row=2, column=0, padx=20, pady=(0,20), sticky="nsew")

    def change_entries(self, table):
        # Destroy the current fields frame
        self.fields.destroy()

        # Creates a new EntryFrames with labels from the other table
        self.fields = EntryFrames(self, labels=self.get_columns(table))
        self.fields.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

    def get_tables(self):
        return list(self.tables_columns.keys())

    def get_columns(self, table):
        return self.tables_columns[table]

    # Entries getter
    def getter(self):
        entries = self.fields.get()
        print(entries)
        return entries

    # Create entry button's function
    def create_entry(self):
        return "Entry created!"

    # Read entry button's function
    def read_entry(self):
        self.getter()

    # Update entry button function
    def update_entry(self):
        return "Entry updated!"

    # Delete entry button's function
    def delete_entry(self):
        return "Entry deleted!"

    # Clear button function
    def clear_entries(self):
        return "Entries cleared!"
        # self.entries.clear()

app = App()
app.mainloop()