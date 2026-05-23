import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkcalendar import DateEntry
from tkinter import messagebox
import sqlite3
import csv
import matplotlib.pyplot as plt

# Connect database
conn = sqlite3.connect("expenses.db")

# Create cursor
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount TEXT,
    category TEXT,
    date TEXT
)
""")

conn.commit()

# Create main window
window = tk.Tk()
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=3)

# Window title
window.title("Smart Expense Tracker")

# Window size
window.geometry("500x400")

# Windows Background set 
window.config(bg="#f0f4f7")

# Function to add expense
def add_expense():

    # Get values from entry fields
    amount = amount_entry.get()
    category = category_entry.get()
    date = date_entry.get()
          # Validation
    # Validation
    if amount == "" or category == "" or date == "":
      messagebox.showerror("Error", "All fields are required")
      return

    # Check amount is numeric
    if not amount.isdigit():
      messagebox.showerror("Error", "Amount must be numeric")
      return
    # Insert data into database
    cursor.execute(
        "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
        (amount, category, date)
    )

    # Save changes
    conn.commit()
    show_expenses()
    update_total()

    # Clear input fields
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

# Function to display expenses

def show_expenses():

    # Clear existing data from table
    for row in expense_table.get_children():
        expense_table.delete(row)

    # Fetch data from database
    cursor.execute("SELECT * FROM expenses")

    records = cursor.fetchall()

    # Insert data into table
    for record in records:

     expense_table.insert(
        "",
        tk.END,
        iid=record[0],
        values=(record[1], record[2], record[3])
    )
     
# Function to calculate total expense

def update_total():

    # Fetch all amounts
    cursor.execute("SELECT amount FROM expenses")

    records = cursor.fetchall()

    total = 0

    # Add all amounts
    for record in records:
        total += int(record[0])

    # Update label text
    total_label.config(text=f"Total Expense: ₹{total}")

# Function to export data to CSV

def export_csv():

    # Fetch all records
    cursor.execute("SELECT * FROM expenses")

    records = cursor.fetchall()

    # Create CSV file
    with open("expenses_report.csv", "w", newline="") as file:

        writer = csv.writer(file)

        # Write headings
        writer.writerow(["ID", "Amount", "Category", "Date"])

        # Write data
        writer.writerows(records)

    # Success message
    messagebox.showinfo(
        "Export Successful",
        "Expenses exported to expenses_report.csv"
    )

# Function for instant search

def search_expense(event):

    # Get typed text
    search_text = search_entry.get()
    if search_text == "":
     show_expenses()
     return

    # Clear existing table
    for row in expense_table.get_children():
        expense_table.delete(row)

    # Search database
    cursor.execute(
        "SELECT * FROM expenses WHERE category LIKE ?",
        ('%' + search_text + '%',)
    )

    records = cursor.fetchall()

    # Display matching records
    for record in records:

        expense_table.insert(
            "",
            tk.END,
            iid=record[0],
            values=(record[1], record[2], record[3])
        )

# Function to show pie chart

def show_chart():

    # Fetch category and amount
    cursor.execute(
        "SELECT category, amount FROM expenses"
    )

    records = cursor.fetchall()

    # Dictionary for category totals
    data = {}

    # Process records
    for category, amount in records:

        amount = int(amount)

        if category in data:
            data[category] += amount
        else:
            data[category] = amount

    # Prepare chart data
    categories = list(data.keys())
    amounts = list(data.values())

    # Create pie chart
    plt.figure(figsize=(6,6))

    plt.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%'
    )

    plt.title("Expense Distribution")

    plt.show()

# Function to delete selected expense

def delete_expense():

    # Get selected item from table
    selected_item = expense_table.selection()

    # Check if something selected
    if selected_item:

        # Get row values
        item = expense_table.item(selected_item)

        # Extract ID
        expense_id = selected_item[0]

        # Delete from database
        cursor.execute(
            "DELETE FROM expenses WHERE id=?",
            (expense_id,)
        )

        # Save changes
        conn.commit()

        # Refresh table
        show_expenses()
        update_total()

        print("Expense Deleted")

# Function for custom category

def custom_category(event):

    # Check selected value
    if category_entry.get() == "Other":

        # Ask user for custom category
        custom = simpledialog.askstring(
            "Custom Category",
            "Enter Category Name"
        )

        # If user entered something
        if custom:

            category_entry.set(custom)

print("Expense Added Successfully")

 

# ---------------- TITLE ----------------
title_label = tk.Label(
    window,
    text="Smart Expense Tracker",
    font=("Arial", 20, "bold"),
    bg="#f0f4f7",
    fg="#333333"
)

title_label.pack(pady=15)

# ---------------- AMOUNT ----------------
amount_label = tk.Label(
    window,
    text="Enter Amount",
    font=("Arial", 11),
    bg="#f0f4f7"
)
amount_label.pack()

amount_entry = tk.Entry(window, width=30)
amount_entry.pack(pady=5)

# ---------------- CATEGORY ----------------
category_label = tk.Label(window,               
    text="Select or Enter Category", 
    font=("Arial", 11),
    bg="#f0f4f7"
    )
category_label.pack()

category_entry = ttk.Combobox(
    window,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Education",
        "Other"
    ]
)

category_entry.pack(pady=5)
category_entry.bind("<<ComboboxSelected>>", custom_category)

# ---------------- DATE ----------------
date_label = tk.Label(window, 
    text="Enter Date",
    font=("Arial", 11),
    bg="#f0f4f7"
    )
date_label.pack()

date_entry = DateEntry(
    window,
    state="readonly",
    width=20,
    background="blue",
    foreground="white",
    borderwidth=2,
    date_pattern="dd-mm-yyyy"
)

date_entry.pack(pady=5)

# ---------------- BUTTONS ----------------

add_button = tk.Button(
    window,
    text="Add Expense",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15,
    command=add_expense
)

add_button.pack(pady=10)
#----------------------------------DELETE BUTON----------------------------------------#

delete_button = tk.Button(
    window,
    text="Delete Expense",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15,
    command=delete_expense
)

delete_button.pack(pady=5)

#----------------------------------CHART BUTON----------------------------------------#

chart_button = tk.Button(
    window,
    text="Show Chart",
    bg="#FF9800",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15,
    command=show_chart
)

chart_button.pack(pady=5)

#----------------------------------EXPORT BUTON----------------------------------------#

export_button = tk.Button(
    window,
    text="Export CSV",
    bg="#2196F3",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15,
    command=export_csv
)

export_button.pack(pady=5)

# Total Expense Label
total_label = tk.Label(
    window,
    text="Total Expense: ₹0",
    font=("Arial", 14, "bold"),
    bg="#f0f4f7",
    fg="green"
)

total_label.pack(pady=10)

# Search Label

search_label = tk.Label(
    window,
    text="Search Category",
    font=("Arial", 11),
    bg="#f0f4f7"
)

search_label.pack()

# Search Entry
search_entry = tk.Entry(window, width=30)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", search_expense)

# Frame for table and scrollbar
table_frame = tk.Frame(window)

table_frame.pack(pady=20)

# Scrollbar
scrollbar = tk.Scrollbar(
    table_frame,
    bg="#4CAF50",
    activebackground="#2E7D32",
    troughcolor="#D3D3D3"
)

# Style for table heading
style = ttk.Style()

style.theme_use("default")

style.configure(
    "Treeview.Heading",
    foreground="red",
    font=("Arial", 11, "bold")
)

# Create table
expense_table = ttk.Treeview(
    table_frame,
    columns=("Amount", "Category", "Date"),
    show="headings",
    height=8,
    yscrollcommand=scrollbar.set
)
scrollbar.config(command=expense_table.yview)

# Headings
expense_table.heading("Amount", text="Amount")
expense_table.heading("Category", text="Category")
expense_table.heading("Date", text="Date")


# Column widths and alignment
expense_table.column("Amount", width=100, anchor="center")
expense_table.column("Category", width=150, anchor="center")
expense_table.column("Date", width=150, anchor="center")

# Show table
expense_table.pack(side=tk.LEFT)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

show_expenses()
update_total()
# Run window
window.mainloop()