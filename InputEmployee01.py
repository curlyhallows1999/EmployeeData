import tkinter as tk 
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# Database connection parameters
host = '10.7.0.20'  # Replace with your MySQL host
database = 'hr'      # Replace with your MySQL database name
user = 'lmsadm_db'   # Replace with your MySQL username
password = 'P@nda#LM%PT'  # Replace with your MySQL password

def check_duplicate_employee(employee_id, connection):
    """ Check if the employee ID already exists in the database. """
    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM employeesmaster WHERE EmployeeID = %s"
        cursor.execute(query, (employee_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        messagebox.showerror("Database Error", str(e))
        return False
    finally:
        cursor.close()
        
def check_duplicate_department(department_name, connection):
    """ Check if the department name already exists in the database. """
    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM department WHERE Department = %s"
        cursor.execute(query, (department_name,))
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        messagebox.showerror("Database Error", str(e))
        return False
    finally:
        cursor.close()

def insert_or_update_department():
    department_name = entry_dept_name.get().strip()  # Get the Department Name

    if not department_name:
        messagebox.showwarning("Input Error", "Please enter a department name.")
        return

    # Add confirmation dialog with input data
    confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to save the department '{department_name}'?")
    if not confirm:
        return  # Exit the function if the user clicks "No"

    try:
        # Establish the connection once
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the department already exists for update or insert
            if check_duplicate_department(department_name, connection):
                # Update the department if it already exists
                query = "UPDATE department SET Department = %s WHERE Department = %s"
                cursor.execute(query, (department_name, department_name))
                connection.commit()
                messagebox.showinfo("Success", "Department updated successfully.")
            else:
                # Insert new department
                query = "INSERT INTO department (Department) VALUES (%s)"
                cursor.execute(query, (department_name,))
                connection.commit()
                messagebox.showinfo("Success", "Department added successfully.")

    except Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        # Ensure connection is closed
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def find_department():
    """ Open a pop-up to input department search term and display matching records. """
    def search_departments():
        filter_pattern = search_entry.get().strip()
        
        if not filter_pattern:
            messagebox.showwarning("Input Error", "Please enter a department name to search.")
            return
        
        try:
            # Establish the connection
            connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )

            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT Department FROM department WHERE Department LIKE %s"
                cursor.execute(query, (filter_pattern + '%',))  # Adjusted to use LIKE with wildcards
                records = cursor.fetchall()

                # Clear the Listbox before inserting new data
                department_listbox.delete(0, tk.END)

                if records:
                    for record in records:
                        department_listbox.insert(tk.END, record[0])

                    # Close the search window if records are found
                    search_window.destroy()
                    
                    # Show the Listbox
                    department_listbox.grid(row=2, column=0, columnspan=4)
                else:
                    messagebox.showwarning("Not Found", f"No departments matching '{filter_pattern}' found.")

        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Create a new Toplevel window for searching
    search_window = tk.Toplevel(root)
    search_window.title("Find Department")
    
    # Make the pop-up window transient to the main window
    search_window.transient(root)

    # Center the pop-up window
    center_window(search_window, 400, 100)
  
    tk.Label(search_window, text="Enter Department Name:").grid(row=0, column=0, padx=10, pady=10)
    search_entry = tk.Entry(search_window, width=30)
    search_entry.grid(row=0, column=1, padx=10, pady=10)

    search_button = tk.Button(search_window, text="Search", command=search_departments)
    search_button.grid(row=1, column=0, columnspan=2, pady=10)

    # Ensure the search window is modal (blocks interaction with the main window)
    search_window.grab_set()
    search_button.grid(row=1, column=0, columnspan=2, pady=10)

def list_departments():
    """ Display all departments in the database using a Listbox. """
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT Department FROM department"
            cursor.execute(query)
            records = cursor.fetchall()

            if records:
                # Clear the Listbox before inserting new data
                department_listbox.delete(0, tk.END)
                for record in records:
                    department_listbox.insert(tk.END, record[0])
                
                # Show the Listbox
                department_listbox.grid(row=2, column=0, columnspan=4)

    except Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def copy_to_clipboard():
    """ Copy the selected department from the Listbox to the clipboard. """
    try:
        selected_department = department_listbox.get(department_listbox.curselection())
        root.clipboard_clear()  # Clear the clipboard
        root.clipboard_append(selected_department)  # Add the selected department to the clipboard
        messagebox.showinfo("Copied", f"Department '{selected_department}' copied to clipboard.")
    except tk.TclError:
        messagebox.showwarning("Selection Error", "Please select a department from the list to copy.")

def delete_department():
    """ Delete the selected department from the database. """
    department_name = entry_dept_name.get().strip()
    
    if not department_name:
        messagebox.showwarning("Input Error", "Please enter a department name to delete.")
        return
    
    confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the department '{department_name}'?")
    if not confirm:
        return  # Exit if user clicks "No"

    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "DELETE FROM department WHERE Department = %s"
            cursor.execute(query, (department_name,))
            connection.commit()
            messagebox.showinfo("Success", "Department deleted successfully.")
            entry_dept_name.delete(0, tk.END)  # Clear the input field after deletion

    except Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def clear_fields():
    """ Clear the input field. """
    entry_dept_name.delete(0, tk.END)  # Clear the entry field
    department_listbox.grid_forget()  # Hide the Listbox

def on_listbox_select(event):
    """ Update the entry field with the selected department from the Listbox and hide the Listbox. """
    try:
        selected_department = department_listbox.get(department_listbox.curselection())
        entry_dept_name.delete(0, tk.END)  # Clear the entry field
        entry_dept_name.insert(0, selected_department)  # Insert the selected department
        department_listbox.grid_forget()  # Hide the Listbox after selection
    except tk.TclError:
        pass  # Do nothing if no item is selected

def center_window(root, width, height):
    """ Centers the window on the screen """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    root.geometry(f"{width}x{height}+{x}+{y}")
    
def save_all():
    employee_id = entry_employee_id.get().strip()
    first_name = entry_first_name.get().strip()
    department = entry_dept_name.get().strip()
    card_number = entry_card_number.get().strip()
    gender = entry_gender.get().strip()

    if not (employee_id and first_name and department and card_number and gender):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if connection.is_connected():
            cursor = connection.cursor()

            if check_duplicate_employee(employee_id, connection):
                messagebox.showwarning("Duplicate Error", "This Employee ID already exists.")
                return

            query = """INSERT INTO employeesmaster 
                       (EmployeeID, FirstName, Department, CardNumber, Gender) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (employee_id, first_name, department, card_number, gender))
            connection.commit()
            messagebox.showinfo("Success", "Employee added successfully.")

    except Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Create the main application window
root = tk.Tk()
root.title("Department Management")

# Set window size and center it
window_width = 888
window_height = 666
center_window(root, window_width, window_height)

# Create input fields
tk.Label(root, text="Department Name:").grid(row=0, column=0)
entry_dept_name = tk.Entry(root, width=88)  # Set the width to enlarge the input field
entry_dept_name.grid(row=0, column=1)

# Create input fields
tk.Label(root, text="Employee ID:").grid(row=4, column=0)
entry_employee_id = tk.Entry(root, width=88)  # Set the width to enlarge the input field
entry_employee_id.grid(row=4, column=1)

# Create input fields
tk.Label(root, text="First Name:").grid(row=5, column=0)
entry_first_name = tk.Entry(root, width=88)  # Set the width to enlarge the input field
entry_first_name.grid(row=5, column=1)

# Create input fields
tk.Label(root, text="Card Number:").grid(row=6, column=0)
entry_card_number = tk.Entry(root, width=88)  # Set the width to enlarge the input field
entry_card_number.grid(row=6, column=1)

# Create input fields
tk.Label(root, text="Gender:").grid(row=7, column=0)
entry_gender = tk.Entry(root, width=88)  # Set the width to enlarge the input field
entry_gender.grid(row=7, column=1)

# Create a frame for buttons to standardize placement
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)  # Add padding to the frame

# Create buttons and display them in the frame
save_button = tk.Button(button_frame, text="Save Department", command=insert_or_update_department)
save_button.grid(row=0, column=0, padx=5)  # Add padding between buttons

find_button = tk.Button(button_frame, text="Find Department", command=find_department)
find_button.grid(row=0, column=1, padx=5)  # Add padding between buttons

list_button = tk.Button(button_frame, text="List Departments", command=list_departments)
list_button.grid(row=0, column=2, padx=5)  # Add padding between buttons

copy_button = tk.Button(button_frame, text="Copy to Clip", command=copy_to_clipboard)
copy_button.grid(row=0, column=3, padx=5)  # Add padding between buttons

delete_button = tk.Button(button_frame, text="Delete Department", command=delete_department)
delete_button.grid(row=0, column=4, padx=5)  # Add padding between buttons

clear_button = tk.Button(button_frame, text="Clear", command=clear_fields)
clear_button.grid(row=0, column=5, padx=5)  # Add padding between buttons

# Listbox to display departments (initially hidden) with enlarged dimensions
department_listbox = tk.Listbox(root, width=80, height=10)

# Bind the listbox selection event to update the entry field
department_listbox.bind("<ButtonRelease-1>", on_listbox_select)

# --- Added save Button ---
save_button = tk.Button(root, text="Save All", command=save_all)
save_button.grid(row=8, column=1)
# --- End of added section ---

# Start the GUI event loop
root.mainloop()
