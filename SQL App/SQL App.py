# Imports
import customtkinter # GUI
from CTkMessagebox import CTkMessagebox # Messages Library
import mysql.connector # MySQL
from collections import defaultdict # Creates Dict

customtkinter.set_appearance_mode("system")  # default

# --------------------------------- Application -----------------------------------------

# Input Dialogs
class Dialog(customtkinter.CTkInputDialog):
    def __init__(self, master, text, title):
        super().__init__(text=text, title=title)
        self.entry = self.get_input()

    def get_entry(self):
        return self.entry

# Tables Frame
class TablesFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.selected_table = master.get_tables(0)

        # Dropdown callback function
        def selected_table(table):
            self.selected_table = table
            # Sets entries to selected table's columns
            master.change_entries(table)

        # Choose table label & it's position
        label = customtkinter.CTkLabel(self, text="Choose table:", fg_color="transparent")
        label.grid(row=0, column=0, padx=20, pady=20)

        # Dropdown to select table & it's position
        optionmenu = customtkinter.CTkOptionMenu(self, values=master.get_tables(""), command=selected_table)
        optionmenu.grid(row=0, column=1, padx=20, pady=20)

# Entries Frame
class EntryFrames(customtkinter.CTkFrame):
    def __init__(self, master, labels):
        super().__init__(master)

        # Labels & entries
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
    def get_entries(self):
        entries_content = {}
        for label, entry in zip(self.labels, self.entries):
            entries_content[label] = entry.get()
        return entries_content

    # Clears fields values
    def clear_fields(self):
        for entry in self.entries:
            entry.delete(0, len(entry.get()))

    # Writes text inside the fields
    def write_fields(self, text):
        self.clear_fields()
        for index, entry in enumerate(self.entries):
            entry.insert(0, text[index])

# CRUD Buttons Frame
class CrudFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Buttons attributes
        self.texts = ["Insert", "Read", "Update", "Delete"]

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
        def insert_entry():
            print(master.insert_entry())
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
            master.clear_fields()

        # List with functions
        functions = [insert_entry, read_entry, update_entry, delete_entry]

        # Creates DML buttons & their positions
        for i, (text, function) in enumerate(zip(self.texts, functions)):
            button = customtkinter.CTkButton(self, width=0.5, text=text, command=function)
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        # Creates Clear Button
        clear_button = customtkinter.CTkButton(self, text="Clear Fields", command=clear_entries)
        clear_button.grid(row=1, columnspan=len(self.texts), padx=10, pady=10, sticky="ew")

# Application Class
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # customtkinter.set_default_color_theme("blue")
        self.title("SQL DML App")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Input Dialogs
        # user = Dialog(self, text="Enter user:", title="MySQL User").get_entry()
        # password = Dialog(self, text="Enter password:", title="MySQL Password").get_entry()

        # print(user, password)

        # Block to get the tables names and their columns

        try:
            
            self.connection_params = {
                "user":'root',
                "password":'password',
                "host":'127.0.0.1',
                "database":'girrafe'
            }

            with self.establish_connection(self.connection_params) as cnx:
                cursor = cnx.cursor(buffered=True)

                # Query to obtain all tables names
                tables_query = ("SHOW TABLES;")

                # Executes query
                cursor.execute(tables_query)

                # Saves the table's names
                tables_names = [table[0] for table in cursor]

                # Empty dict with empty lists values
                self.tables_columns = defaultdict(list)

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
                    self.tables_columns[name].extend(column[0] for column in columns)

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        # Tables Frame
        self.tables = TablesFrame(self)
        self.tables.grid(row=0, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Fields Frame
        self.fields = EntryFrames(self, labels=self.get_columns(self.tables.selected_table))
        self.fields.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Buttons Frame
        self.crud_buttons = CrudFrame(self)
        self.crud_buttons.grid(row=2, column=0, padx=20, pady=(0,20), sticky="nsew")

    # Establish connection to MySQL Server (local)
    def establish_connection(self, params):
        return mysql.connector.connect(**params)
    
    # Change the entry fields based on the selected table by the dropdown
    def change_entries(self, table):
        # Destroy the current fields frame
        self.fields.destroy()

        # Creates a new EntryFrames with labels from the other table
        self.fields = EntryFrames(self, labels=self.get_columns(table))
        self.fields.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

    # Returns DB's tables based on index
    def get_tables(self, index):
        tables = list(self.tables_columns.keys())
        return tables[index] if isinstance(index, int) else tables[:]

    # Returns the given table's columns
    def get_columns(self, table):
        return self.tables_columns[table]

    # Create entry button's function
    def insert_entry(self):
        try:
            # Tries to connect to MySQL Server
            with self.establish_connection(self.connection_params) as cnx:
                cursor = cnx.cursor(buffered=True)

                entries = self.fields.get_entries()
                table = self.tables.selected_table

                # Gets the registry
                insert_query = (f"INSERT INTO `{table}` VALUES{tuple(entries.values())};")

                try:
                    # Tries to execute query
                    cursor.execute(insert_query)
                    
                    # Success message
                    CTkMessagebox(title="Success", message="Registry sucessfully added!", icon="check", option_1="Close")
                    
                    # Commit the transaction to make the changes permanent
                    cnx.commit()
                except Exception as error:
                    # Error message
                    CTkMessagebox(title="Error", message=f"Error adding registry:\n'{error}'", icon="warning")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Read entry button's function
    def read_entry(self):
        try:
            # Tries to connect to MySQL Server
            with self.establish_connection(self.connection_params) as cnx:
                cursor = cnx.cursor(buffered=True)
            
                entries = self.fields.get_entries()
                table = self.tables.selected_table

                for key, value in entries.items():
                    if value:
                        entered_entry = key
                        break

                # Gets the registry
                registry_query = (
                        f"""
                        SELECT *
                        FROM `{table}`
                        WHERE `{entered_entry}` = %s
                        LIMIT 1;
                        """
                )

                # Tries to execute query
                cursor.execute(registry_query, [entries[entered_entry]])

                # Saves the entry
                try:
                    registry = [registry for registry in cursor][0]

                    # Returns the registry and writes it's content into the fields 
                    return self.fields.write_fields(registry)
                except Exception as error:
                    CTkMessagebox(title="Error", message="Registry not found", icon="warning")
                    print(error)

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Update entry button function
    def update_entry(self):
        return "Entry updated!"

    # Delete entry button's function
    def delete_entry(self):
        msg = CTkMessagebox(title="Delete", message="Do you want to destroy the current entry?", option_1="No", option_2="Yes", icon="warning")
        if msg.get() == "Yes":
            try:
                # Tries to connect to MySQL Server
                with self.establish_connection(self.connection_params) as cnx:
                    cursor = cnx.cursor(buffered=True)

                    entries = self.fields.get_entries()
                    table = self.tables.selected_table
                    id_field = next(iter(entries))

                    if all(entries.values()):
                        # Gets the registry
                        delete_query = (
                                f"""
                                DELETE
                                FROM `{table}`
                                WHERE `{id_field}` = %s;
                                """
                        )

                        try:
                            # Tries to execute query
                            cursor.execute(delete_query, list(entries[id_field]))

                            # Commit the transaction to make the changes permanent
                            cnx.commit()

                            # Success Messagebox 
                            return CTkMessagebox(title="Success", message=f"The entry on table '{table}' by id '{entries[id_field]}' was successfully deleted.", icon="check", option_1="Close")
                        except Exception as error:
                            # Error Messagebox
                            return CTkMessagebox(title="Error", message=f"ERROR!\n {error}", icon="cancel", option_1="Close")
                    else:
                        return CTkMessagebox(title="Error", message="ERROR! Check that all fields are filled correctly.\nRecommended: Use the Read button before delete.", icon="cancel", option_1="Close")
            except mysql.connector.Error as err:
                print(f"Error: {err}")

    # Clear button function
    def clear_fields(self):
        self.fields.clear_fields()

if __name__ == "__main__":
    app = App()
    app.mainloop()